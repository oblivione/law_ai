import openai
import httpx
import json
from typing import List, Dict, Any, Optional
from loguru import logger
import asyncio
import re

from app.core.config import settings
from app.schemas.search import LegalAnalysisResponse

class AIAnalyzer:
    """Handles AI-powered document analysis and legal reasoning using OpenRouter"""
    
    def __init__(self):
        # Configure OpenAI client for OpenRouter
        openai.api_key = settings.OPENROUTER_API_KEY
        openai.api_base = settings.OPENROUTER_BASE_URL
        
        # HTTP client for direct API calls
        self.http_client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://legal-ai-platform.com",
                "X-Title": "Legal Document Analysis Platform"
            }
        )
        
        logger.info("AIAnalyzer initialized with OpenRouter integration")
    
    async def perform_legal_reasoning(
        self,
        query: str,
        context: List[str],
        analysis_type: str = "general",
        include_citations: bool = True,
        include_counterarguments: bool = True
    ) -> LegalAnalysisResponse:
        """Perform comprehensive legal analysis using AI reasoning"""
        
        try:
            # Prepare context from relevant documents
            context_text = "\n\n".join(context[:10])  # Limit context length
            
            # Build system prompt based on analysis type
            system_prompt = self._build_system_prompt(analysis_type, include_citations, include_counterarguments)
            
            # Build user prompt
            user_prompt = f"""
            Legal Query: {query}
            
            Relevant Legal Documents and Context:
            {context_text}
            
            Please provide a comprehensive legal analysis addressing the query based on the provided context.
            """
            
            # Make API call
            response = await self._make_openrouter_call(
                model=settings.REASONING_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse response
            analysis_text = response.get("content", "")
            
            # Extract structured information from response
            key_points = self._extract_key_points(analysis_text)
            citations = self._extract_citations_from_analysis(analysis_text)
            precedents = self._extract_precedents(analysis_text)
            counterarguments = self._extract_counterarguments(analysis_text) if include_counterarguments else []
            reasoning_chain = self._extract_reasoning_chain(analysis_text)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(analysis_text, context)
            
            return LegalAnalysisResponse(
                query=query,
                analysis=analysis_text,
                key_points=key_points,
                relevant_citations=citations,
                precedents=precedents,
                counterarguments=counterarguments,
                confidence_score=confidence_score,
                sources_used=[],  # Would be populated with actual document IDs
                reasoning_chain=reasoning_chain
            )
            
        except Exception as e:
            logger.error(f"Error in legal reasoning: {str(e)}")
            raise e
    
    async def analyze_document(self, text: str, document_type: str = "unknown") -> Dict[str, Any]:
        """Analyze a single document to extract legal metadata and insights"""
        
        try:
            system_prompt = """You are a legal document analyzer. Extract and analyze the following from the provided legal text:
            
            1. Document type and jurisdiction
            2. Key legal concepts and principles
            3. Important citations and references
            4. Main arguments and holdings
            5. Relevant legal entities (parties, judges, etc.)
            6. Summary of the document
            7. Legal significance and implications
            
            Provide your analysis in a structured JSON format."""
            
            user_prompt = f"""
            Document Type: {document_type}
            
            Legal Text:
            {text[:4000]}  # Limit text length
            
            Please analyze this legal document and provide structured output.
            """
            
            response = await self._make_openrouter_call(
                model=settings.DOCUMENT_ANALYSIS_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            # Parse response (try to extract JSON or structure the text)
            analysis_text = response.get("content", "")
            return self._parse_document_analysis(analysis_text)
            
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            return {}
    
    async def generate_document_summary(
        self,
        content: str,
        summary_type: str = "comprehensive",
        max_length: int = 1000
    ) -> str:
        """Generate AI-powered summary of a document"""
        
        try:
            system_prompts = {
                "comprehensive": "You are a legal document summarizer. Create a comprehensive summary that covers all key points, legal principles, and implications.",
                "executive": "You are creating an executive summary for legal professionals. Focus on the most critical points and practical implications.",
                "key_points": "You are extracting key points from a legal document. Present only the most essential legal concepts and holdings."
            }
            
            system_prompt = system_prompts.get(summary_type, system_prompts["comprehensive"])
            
            user_prompt = f"""
            Please create a {summary_type} summary of the following legal document (max {max_length} words):
            
            {content[:6000]}  # Limit content length
            
            Summary:
            """
            
            response = await self._make_openrouter_call(
                model=settings.DOCUMENT_ANALYSIS_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=max_length // 3  # Rough token estimation
            )
            
            return response.get("content", "")
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return ""
    
    async def extract_legal_entities(
        self,
        content: str,
        entity_types: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """Extract legal entities from document content"""
        
        default_types = ["parties", "judges", "courts", "statutes", "cases", "regulations"]
        types_to_extract = entity_types or default_types
        
        try:
            system_prompt = f"""You are a legal entity extractor. Extract the following types of entities from the legal text:
            {', '.join(types_to_extract)}
            
            Return the results in JSON format with entity types as keys and lists of entities as values."""
            
            user_prompt = f"""
            Extract legal entities from this text:
            
            {content[:4000]}
            
            Entities:
            """
            
            response = await self._make_openrouter_call(
                model=settings.DOCUMENT_ANALYSIS_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            # Parse JSON response or extract entities manually
            return self._parse_entities_response(response.get("content", ""))
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return {}
    
    async def compare_documents(
        self,
        documents: List[Dict[str, Any]],
        comparison_type: str = "similarity"
    ) -> Dict[str, Any]:
        """Compare multiple legal documents"""
        
        try:
            # Prepare document texts
            doc_texts = []
            for i, doc in enumerate(documents):
                doc_text = f"Document {i+1} (ID: {doc['id']}):\n{doc['content'][:2000]}\n"
                doc_texts.append(doc_text)
            
            combined_text = "\n\n".join(doc_texts)
            
            system_prompts = {
                "similarity": "You are comparing legal documents for similarities. Identify common themes, legal principles, and overlapping content.",
                "differences": "You are comparing legal documents for differences. Highlight contrasting positions, different legal approaches, and unique aspects.",
                "legal_alignment": "You are analyzing legal alignment between documents. Assess consistency, conflicts, and legal coherence."
            }
            
            system_prompt = system_prompts.get(comparison_type, system_prompts["similarity"])
            
            user_prompt = f"""
            Compare these legal documents based on {comparison_type}:
            
            {combined_text}
            
            Analysis:
            """
            
            response = await self._make_openrouter_call(
                model=settings.REASONING_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            return {
                "comparison_type": comparison_type,
                "analysis": response.get("content", ""),
                "documents_compared": len(documents)
            }
            
        except Exception as e:
            logger.error(f"Error comparing documents: {str(e)}")
            return {}
    
    async def generate_legal_brief(
        self,
        topic: str,
        relevant_documents: List[str],
        brief_type: str = "research",
        jurisdiction: Optional[str] = None,
        max_length: int = 2000
    ) -> str:
        """Generate a legal brief on a specific topic"""
        
        try:
            # Prepare context
            context = "\n\n".join(relevant_documents[:8])  # Limit context
            
            system_prompts = {
                "research": "You are writing a legal research brief. Provide comprehensive analysis with citations and legal precedents.",
                "argument": "You are writing a legal argument brief. Structure your argument logically with strong legal support.",
                "motion": "You are writing a motion brief. Follow proper legal motion format and structure."
            }
            
            system_prompt = system_prompts.get(brief_type, system_prompts["research"])
            
            jurisdiction_text = f" in {jurisdiction}" if jurisdiction else ""
            
            user_prompt = f"""
            Topic: {topic}
            Brief Type: {brief_type}
            Jurisdiction: {jurisdiction or "General"}
            Max Length: {max_length} words
            
            Relevant Legal Sources:
            {context}
            
            Please write a {brief_type} brief on "{topic}"{jurisdiction_text} based on the provided legal sources:
            """
            
            response = await self._make_openrouter_call(
                model=settings.REASONING_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=max_length // 3
            )
            
            return response.get("content", "")
            
        except Exception as e:
            logger.error(f"Error generating brief: {str(e)}")
            return ""
    
    async def generate_document_analytics(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analytics and insights for a document"""
        
        try:
            # This would be a complex analysis combining various metrics
            # For now, return basic analytics structure
            analytics = {
                "document_id": document.get("id"),
                "readability_score": 0.0,  # Would calculate actual readability
                "complexity_score": 0.0,   # Legal complexity analysis
                "citation_count": 0,       # Number of citations
                "concept_density": 0.0,    # Legal concept density
                "sentiment_analysis": {    # Legal sentiment
                    "tone": "neutral",
                    "confidence": 0.0
                },
                "key_themes": [],          # Main themes
                "legal_risk_indicators": [], # Risk analysis
                "recommendations": []      # AI recommendations
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating analytics: {str(e)}")
            return {}
    
    async def _make_openrouter_call(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Make API call to OpenRouter"""
        
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = await self.http_client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("choices") and result["choices"][0].get("message"):
                return {"content": result["choices"][0]["message"]["content"]}
            else:
                logger.error(f"Unexpected API response structure: {result}")
                return {"content": ""}
                
        except Exception as e:
            logger.error(f"OpenRouter API call failed: {str(e)}")
            raise e
    
    def _build_system_prompt(self, analysis_type: str, include_citations: bool, include_counterarguments: bool) -> str:
        """Build system prompt based on analysis parameters"""
        
        base_prompt = "You are an expert legal analyst with deep knowledge of law and legal reasoning. "
        
        type_prompts = {
            "general": "Provide comprehensive legal analysis covering all relevant aspects.",
            "case_law": "Focus on case law analysis, precedents, and judicial reasoning.",
            "statute": "Focus on statutory interpretation, legislative intent, and regulatory analysis.",
            "precedent": "Focus on precedential value, distinguishing cases, and legal evolution."
        }
        
        analysis_prompt = type_prompts.get(analysis_type, type_prompts["general"])
        
        additional_instructions = []
        if include_citations:
            additional_instructions.append("Include relevant legal citations and references.")
        if include_counterarguments:
            additional_instructions.append("Consider potential counterarguments and alternative interpretations.")
        
        full_prompt = f"{base_prompt}{analysis_prompt}"
        if additional_instructions:
            full_prompt += f" {' '.join(additional_instructions)}"
        
        return full_prompt
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from analysis text"""
        # Simple extraction based on patterns
        lines = text.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            if (line.startswith(('•', '-', '*')) or 
                line.startswith(('Key point', 'Important', 'Note that')) or
                re.match(r'^\d+\.', line)):
                key_points.append(line.lstrip('•-* '))
        
        return key_points[:10]  # Limit to top 10
    
    def _extract_citations_from_analysis(self, text: str) -> List[str]:
        """Extract legal citations from analysis text"""
        # Basic citation patterns
        patterns = [
            r'\d+\s+[A-Z][a-z]+\.?\s+\d+',
            r'\d+\s+U\.S\.C\.?\s+§?\s*\d+',
            r'\d+\s+F\.?\s*\d*d?\s+\d+',
        ]
        
        citations = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            citations.extend(matches)
        
        return list(set(citations))
    
    def _extract_precedents(self, text: str) -> List[str]:
        """Extract legal precedents from analysis text"""
        # Look for case names and precedent indicators
        case_pattern = r'([A-Z][a-zA-Z\s&.,-]+)\s+v\.?\s+([A-Z][a-zA-Z\s&.,-]+)'
        matches = re.findall(case_pattern, text)
        
        precedents = []
        for match in matches:
            case_name = f"{match[0].strip()} v. {match[1].strip()}"
            if len(case_name) < 100:
                precedents.append(case_name)
        
        return list(set(precedents))
    
    def _extract_counterarguments(self, text: str) -> List[str]:
        """Extract counterarguments from analysis text"""
        # Look for counterargument indicators
        counter_patterns = [
            r'However[,\s]+([^.]+\.)',
            r'On the other hand[,\s]+([^.]+\.)',
            r'Alternatively[,\s]+([^.]+\.)',
            r'Critics might argue[,\s]+([^.]+\.)'
        ]
        
        counterarguments = []
        for pattern in counter_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            counterarguments.extend(matches)
        
        return counterarguments
    
    def _extract_reasoning_chain(self, text: str) -> List[str]:
        """Extract reasoning chain from analysis text"""
        # Simple approach: look for numbered or sequential reasoning
        lines = text.split('\n')
        reasoning_steps = []
        
        for line in lines:
            line = line.strip()
            if (re.match(r'^(First|Second|Third|Fourth|Fifth|Next|Finally)', line, re.IGNORECASE) or
                re.match(r'^\d+\.', line) or
                'therefore' in line.lower() or 'because' in line.lower()):
                reasoning_steps.append(line)
        
        return reasoning_steps
    
    def _calculate_confidence_score(self, analysis: str, context: List[str]) -> float:
        """Calculate confidence score for the analysis"""
        # Simple heuristic-based confidence calculation
        score = 0.5  # Base score
        
        # Increase score based on analysis quality indicators
        if len(analysis) > 500:
            score += 0.1
        if 'citation' in analysis.lower():
            score += 0.1
        if len(context) > 3:
            score += 0.1
        if any(word in analysis.lower() for word in ['precedent', 'case law', 'statute']):
            score += 0.1
        
        return min(score, 1.0)
    
    def _parse_document_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse document analysis response into structured data"""
        # Try to extract JSON or create structure from text
        try:
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback to text parsing
        return {
            "analysis": analysis_text,
            "document_type": "unknown",
            "key_concepts": [],
            "citations": [],
            "summary": analysis_text[:500] + "..." if len(analysis_text) > 500 else analysis_text
        }
    
    def _parse_entities_response(self, response_text: str) -> Dict[str, List[str]]:
        """Parse entities extraction response"""
        try:
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback parsing
        return {
            "parties": [],
            "judges": [],
            "courts": [],
            "statutes": [],
            "cases": [],
            "regulations": []
        } 