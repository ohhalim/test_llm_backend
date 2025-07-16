"""LangGraph를 사용한 AI 에이전트 그래프 구현"""

from typing import Dict, Any, List, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
import os
from dotenv import load_dotenv

from .tools import vector_tools, api_tools
from .prompts import GENERATE_ANSWER_PROMPT, SUMMARY_PROMPT, QUERY_EXPANSION_PROMPT

load_dotenv()

class AgentState(TypedDict):
    """에이전트의 상태를 정의하는 TypedDict"""
    user_id: int
    query: str
    expanded_query: str
    context: List[Dict[str, Any]]
    answer: str
    error: str
    metadata: Dict[str, Any]

class KnowledgeAgentGraph:
    """지식 공유 게시판 AI 에이전트 그래프"""
    
    def __init__(self):
        # Gemini AI 모델 초기화
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.3
        )
        
        # 그래프 생성
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """LangGraph 그래프 생성"""
        # 상태 그래프 초기화
        workflow = StateGraph(AgentState)
        
        # 노드 추가
        workflow.add_node("expand_query", self.expand_query_node)
        workflow.add_node("retrieve_posts", self.retrieve_posts_node)
        workflow.add_node("generate_answer", self.generate_answer_node)
        workflow.add_node("save_interaction", self.save_interaction_node)
        
        # 엣지 정의 (노드 간 연결)
        workflow.set_entry_point("expand_query")
        workflow.add_edge("expand_query", "retrieve_posts")
        workflow.add_edge("retrieve_posts", "generate_answer")
        workflow.add_edge("generate_answer", "save_interaction")
        workflow.add_edge("save_interaction", END)
        
        # 조건부 엣지 (에러 처리)
        workflow.add_conditional_edges(
            "retrieve_posts",
            self._should_continue_after_retrieval,
            {
                "continue": "generate_answer",
                "no_context": "generate_answer"  # 컨텍스트가 없어도 일반적인 답변 시도
            }
        )
        
        return workflow.compile()
    
    def _should_continue_after_retrieval(self, state: AgentState) -> str:
        """검색 후 다음 단계 결정"""
        if state["error"]:
            return "error"
        return "continue" if state["context"] else "no_context"
    
    async def expand_query_node(self, state: AgentState) -> AgentState:
        """1단계: 쿼리 확장 및 최적화"""
        try:
            # 쿼리 확장 프롬프트 실행
            prompt = QUERY_EXPANSION_PROMPT.format(query=state["query"])
            response = await self.llm.ainvoke(prompt)
            
            state["expanded_query"] = response.content.strip()
            print(f"Query expanded: {state['query']} -> {state['expanded_query']}")
            
        except Exception as e:
            print(f"Error in expand_query_node: {e}")
            state["expanded_query"] = state["query"]  # 실패 시 원본 쿼리 사용
            
        return state
    
    async def retrieve_posts_node(self, state: AgentState) -> AgentState:
        """2단계: 관련 게시글 및 의료 지식 검색"""
        try:
            search_query = state.expanded_query or state.query
            all_context = []
            
            # 1. 일반 게시글 검색
            if state.user_id:
                user_posts = vector_tools.search_similar_posts(
                    query=search_query,
                    user_id=state.user_id,
                    limit=3
                )
                
                # 사용자별 결과가 충분하지 않으면 전체 검색
                if len(user_posts) < 2:
                    global_posts = vector_tools.search_similar_posts(
                        query=search_query,
                        limit=3
                    )
                    # 중복 제거하며 병합
                    existing_ids = {post['metadata']['post_id'] for post in user_posts}
                    for post in global_posts:
                        if post['metadata']['post_id'] not in existing_ids:
                            user_posts.append(post)
                            if len(user_posts) >= 3:
                                break
                
                all_context.extend(user_posts)
            else:
                # 전체 검색
                posts = vector_tools.search_similar_posts(
                    query=search_query,
                    limit=3
                )
                all_context.extend(posts)
            
            # 2. 의료 지식 검색 (의료 관련 질문인 경우)
            medical_keywords = ['의료', '병원', '치료', '진료', '환자', '질병', '증상', '약물', '수술', '검사', '진단']
            if any(keyword in search_query for keyword in medical_keywords):
                medical_results = vector_tools.search_medical_knowledge(
                    query=search_query,
                    limit=3
                )
                
                # 의료 지식 결과를 일반 게시글과 구분하여 추가
                for result in medical_results:
                    result['metadata']['source_type'] = 'medical_knowledge'
                    all_context.append(result)
            
            state.context = all_context
            print(f"Retrieved {len(state.context)} relevant items (posts + medical knowledge)")
            
        except Exception as e:
            print(f"Error in retrieve_posts_node: {e}")
            state.error = f"검색 중 오류가 발생했습니다: {str(e)}"
            
        return state
    
    async def generate_answer_node(self, state: AgentState) -> AgentState:
        """3단계: AI 답변 생성"""
        try:
            # 컨텍스트 준비
            if state.context:
                context_text = ""
                for i, item in enumerate(state.context, 1):
                    metadata = item['metadata']
                    content = item['content']
                    score = item.get('similarity_score', 0)
                    source_type = metadata.get('source_type', 'post')
                    
                    if source_type == 'medical_knowledge':
                        context_text += f"\\n[의료 지식 {i}]\\n"
                        context_text += f"출처: {metadata.get('source', 'N/A')}\\n"
                        context_text += f"분야: {metadata.get('domain', 'N/A')}\\n"
                        context_text += f"유형: {metadata.get('type', 'N/A')}\\n"
                    else:
                        context_text += f"\\n[게시글 {i}]\\n"
                        context_text += f"제목: {metadata.get('title', 'N/A')}\\n"
                    
                    context_text += f"관련도: {score:.2f}\\n" if score else ""
                    context_text += f"내용: {content}\\n"
                    context_text += "-" * 50 + "\\n"
            else:
                context_text = "관련된 게시글이나 의료 지식을 찾을 수 없습니다."
            
            # 답변 생성 프롬프트 실행
            prompt = GENERATE_ANSWER_PROMPT.format(
                query=state.query,
                context=context_text
            )
            
            response = await self.llm.ainvoke(prompt)
            state.answer = response.content.strip()
            
            # 메타데이터 업데이트
            state.metadata.update({
                "context_count": len(state.context),
                "has_relevant_context": len(state.context) > 0
            })
            
            print(f"Answer generated successfully")
            
        except Exception as e:
            print(f"Error in generate_answer_node: {e}")
            state.error = f"답변 생성 중 오류가 발생했습니다: {str(e)}"
            state.answer = "죄송합니다. 답변을 생성하는 중에 오류가 발생했습니다."
            
        return state
    
    async def save_interaction_node(self, state: AgentState) -> AgentState:
        """4단계: 상호작용 기록 저장"""
        try:
            if state.user_id:
                await api_tools.save_interaction(
                    user_id=state.user_id,
                    query=state.query,
                    answer=state.answer
                )
            print("Interaction saved successfully")
            
        except Exception as e:
            print(f"Error in save_interaction_node: {e}")
            # 상호작용 저장 실패는 전체 프로세스에 영향을 주지 않음
            
        return state
    
    async def chat(self, query: str, user_id: int = None) -> Dict[str, Any]:
        """사용자 질문에 대한 AI 채팅 응답"""
        # 초기 상태 설정
        initial_state: AgentState = {
            "user_id": user_id,
            "query": query,
            "expanded_query": "",
            "context": [],
            "answer": "",
            "error": "",
            "metadata": {}
        }
        
        # 그래프 실행
        final_state = await self.graph.ainvoke(initial_state)
        
        # 결과 반환
        return {
            "answer": final_state["answer"],
            "context": final_state["context"],
            "metadata": final_state["metadata"],
            "error": final_state["error"]
        }
    
    async def generate_summary(self, user_id: int) -> str:
        """사용자의 게시글 요약 생성"""
        try:
            # 사용자 게시글 가져오기
            user_posts = await api_tools.get_user_posts(user_id, size=20)
            
            if not user_posts:
                return "분석할 게시글이 없습니다."
            
            # 게시글 텍스트 준비
            posts_text = ""
            for post in user_posts:
                posts_text += f"제목: {post.get('title', 'N/A')}\\n"
                posts_text += f"내용: {post.get('content', 'N/A')}\\n"
                posts_text += "-" * 30 + "\\n"
            
            # 요약 생성
            prompt = SUMMARY_PROMPT.format(posts=posts_text)
            response = await self.llm.ainvoke(prompt)
            
            return response.content.strip()
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"요약 생성 중 오류가 발생했습니다: {str(e)}"

# 전역 에이전트 인스턴스
knowledge_agent = KnowledgeAgentGraph()