import inspect
from typing import Optional, Any, List, Dict
from app.core.config import settings
from app.core.logging import logger
from app.services.hindsight.client import get_hindsight_client
from app.services.hindsight.models import HindsightStatus, HindsightMemoryStatus


class HindsightService:
    def __init__(self):
        self.bank_id = settings.HINDSIGHT_BANK_ID or "deal-intelligence-global"
        self._bank_verified = False

    async def get_status(self) -> HindsightStatus:
        if not settings.HINDSIGHT_API_KEY or not settings.HINDSIGHT_API_KEY.strip():
            return HindsightStatus.NOT_CONFIGURED

        client = get_hindsight_client()
        if not client:
            return HindsightStatus.NOT_CONFIGURED

        try:
            if hasattr(client, "aget_version"):
                res = client.aget_version()
                if inspect.isawaitable(res):
                    await res
            elif hasattr(client, "aget_bank_config"):
                res = client.aget_bank_config(self.bank_id)
                if inspect.isawaitable(res):
                    await res
            elif hasattr(client, "get_version"):
                res = client.get_version()
                if inspect.isawaitable(res):
                    await res
            elif hasattr(client, "get_bank_config"):
                res = client.get_bank_config(self.bank_id)
                if inspect.isawaitable(res):
                    await res
            return HindsightStatus.AVAILABLE
        except Exception as e:
            logger.warning(f"Hindsight health check ping failed: {str(e)}")
            return HindsightStatus.UNAVAILABLE

    async def ensure_bank_exists(self) -> bool:
        if self._bank_verified:
            return True

        client = get_hindsight_client()
        if not client:
            return False

        try:
            logger.info(f"Ensuring Hindsight memory bank exists: bank_id={self.bank_id}")
            if hasattr(client, "acreate_bank"):
                res = client.acreate_bank(
                    bank_id=self.bank_id,
                    name="Deal Intelligence Agent",
                    background="Persistent sales experience memory for analyzing customer interactions, objections, competitors, stakeholders, decisions, actions, and outcomes across deals."
                )
                if inspect.isawaitable(res):
                    await res
            else:
                client.create_bank(
                    bank_id=self.bank_id,
                    name="Deal Intelligence Agent",
                    background="Persistent sales experience memory for analyzing customer interactions, objections, competitors, stakeholders, decisions, actions, and outcomes across deals."
                )
            self._bank_verified = True
            return True
        except Exception as e:
            err_msg = str(e).lower()
            if "already exists" in err_msg or "conflict" in err_msg or "409" in err_msg:
                logger.info(f"Hindsight memory bank already exists: bank_id={self.bank_id}")
                self._bank_verified = True
                return True
            logger.warning(f"Failed to verify/create Hindsight memory bank: {str(e)}")
            return False

    def build_interaction_memory_content(
        self,
        deal_name: str,
        company_name: str,
        deal_stage: str,
        deal_value: Any,
        deal_currency: str,
        interaction_type: str,
        interaction_title: str,
        interaction_content: str,
        contact_name: Optional[str] = None
    ) -> str:
        contact_info = f" with stakeholder {contact_name}" if contact_name else ""
        stage_str = deal_stage.value if hasattr(deal_stage, "value") else str(deal_stage)
        type_str = interaction_type.value if hasattr(interaction_type, "value") else str(interaction_type)

        memory_text = (
            f"Deal '{deal_name}' (Company: '{company_name}', Stage: {stage_str}, Value: ${deal_value} {deal_currency}). "
            f"During a {type_str}{contact_info} titled '{interaction_title}': {interaction_content}"
        )
        return memory_text

    async def retain_interaction(
        self,
        deal_id: str,
        deal_name: str,
        company_name: str,
        deal_stage: str,
        deal_value: Any,
        deal_currency: str,
        interaction_id: str,
        interaction_type: str,
        interaction_title: str,
        interaction_content: str,
        contact_name: Optional[str] = None
    ) -> HindsightMemoryStatus:
        status = await self.get_status()
        if status == HindsightStatus.NOT_CONFIGURED:
            logger.info("Hindsight not configured. Skipping RETAIN execution.")
            return HindsightMemoryStatus(
                status="not_configured",
                bank_id=self.bank_id,
                message="Hindsight API key is not configured in environment."
            )
        elif status == HindsightStatus.UNAVAILABLE:
            logger.warning("Hindsight Cloud service unavailable during retain operation.")
            return HindsightMemoryStatus(
                status="unavailable",
                bank_id=self.bank_id,
                message="Hindsight Cloud memory service is currently unreachable."
            )

        client = get_hindsight_client()
        if not client:
            return HindsightMemoryStatus(
                status="not_configured",
                bank_id=self.bank_id,
                message="Hindsight client instance not available."
            )

        await self.ensure_bank_exists()

        content = self.build_interaction_memory_content(
            deal_name=deal_name,
            company_name=company_name,
            deal_stage=deal_stage,
            deal_value=deal_value,
            deal_currency=deal_currency,
            interaction_type=interaction_type,
            interaction_title=interaction_title,
            interaction_content=interaction_content,
            contact_name=contact_name
        )

        stage_str = deal_stage.value if hasattr(deal_stage, "value") else str(deal_stage)
        type_str = interaction_type.value if hasattr(interaction_type, "value") else str(interaction_type)

        try:
            logger.info(f"Hindsight retain started | bank_id={self.bank_id} | interaction_id={interaction_id}")
            if hasattr(client, "aretain"):
                res = client.aretain(
                    bank_id=self.bank_id,
                    content=content,
                    context=f"deal:{deal_id}",
                    metadata={
                        "deal_id": deal_id,
                        "company": company_name,
                        "stage": stage_str,
                        "interaction_id": interaction_id
                    },
                    tags=[
                        f"deal:{deal_id}",
                        f"stage:{stage_str.lower()}",
                        f"type:{type_str.lower()}"
                    ]
                )
                if inspect.isawaitable(res):
                    res = await res
            else:
                res = client.retain(
                    bank_id=self.bank_id,
                    content=content,
                    context=f"deal:{deal_id}",
                    metadata={
                        "deal_id": deal_id,
                        "company": company_name,
                        "stage": stage_str,
                        "interaction_id": interaction_id
                    },
                    tags=[
                        f"deal:{deal_id}",
                        f"stage:{stage_str.lower()}",
                        f"type:{type_str.lower()}"
                    ]
                )
            logger.info(f"Hindsight retain succeeded | bank_id={self.bank_id} | interaction_id={interaction_id}")
            
            memory_id = getattr(res, "id", None) or "retained"
            return HindsightMemoryStatus(
                status="stored",
                bank_id=self.bank_id,
                memory_ids=[memory_id]
            )
        except Exception as e:
            logger.error(f"Hindsight retain failed for interaction_id={interaction_id}: {str(e)}")
            return HindsightMemoryStatus(
                status="error",
                bank_id=self.bank_id,
                message=f"Memory storage failed: {str(e)}"
            )

    def build_outcome_memory_content(
        self,
        deal_name: str,
        company_name: str,
        deal_stage: str,
        recommendation_title: str,
        recommendation_reasoning: Optional[str],
        action_description: str,
        action_status: str,
        outcome_type: str,
        outcome_description: str,
        impact: Optional[str] = None
    ) -> str:
        stage_str = deal_stage.value if hasattr(deal_stage, "value") else str(deal_stage)
        reasoning_str = f" because {recommendation_reasoning}" if recommendation_reasoning else ""
        impact_str = f" Key impact: {impact}." if impact else ""

        memory_text = (
            f"{company_name} - Deal '{deal_name}' was in stage '{stage_str}'. "
            f"The AI agent recommended '{recommendation_title}'{reasoning_str}. "
            f"The sales team accepted and took action: '{action_description}' (Status: {action_status}). "
            f"Outcome ({outcome_type}): {outcome_description}.{impact_str} "
            f"This historical outcome provides persistent experience on the effectiveness of this recommendation in this context."
        )
        return memory_text

    async def retain_outcome(
        self,
        deal_id: str,
        deal_name: str,
        company_name: str,
        deal_stage: str,
        recommendation_title: str,
        recommendation_reasoning: Optional[str],
        action_description: str,
        action_status: str,
        outcome_type: str,
        outcome_description: str,
        impact: Optional[str] = None,
        company_id: Optional[str] = None
    ) -> HindsightMemoryStatus:
        status = await self.get_status()
        if status == HindsightStatus.NOT_CONFIGURED:
            logger.info("Hindsight not configured. Skipping outcome RETAIN execution.")
            return HindsightMemoryStatus(
                status="not_configured",
                bank_id=self.bank_id,
                message="Hindsight API key is not configured in environment."
            )
        elif status == HindsightStatus.UNAVAILABLE:
            logger.warning("Hindsight Cloud service unavailable during outcome retain operation.")
            return HindsightMemoryStatus(
                status="unavailable",
                bank_id=self.bank_id,
                message="Hindsight Cloud memory service is currently unreachable."
            )

        client = get_hindsight_client()
        if not client:
            return HindsightMemoryStatus(
                status="not_configured",
                bank_id=self.bank_id,
                message="Hindsight client instance not available."
            )

        await self.ensure_bank_exists()

        content = self.build_outcome_memory_content(
            deal_name=deal_name,
            company_name=company_name,
            deal_stage=deal_stage,
            recommendation_title=recommendation_title,
            recommendation_reasoning=recommendation_reasoning,
            action_description=action_description,
            action_status=action_status,
            outcome_type=outcome_type,
            outcome_description=outcome_description,
            impact=impact
        )

        stage_str = deal_stage.value if hasattr(deal_stage, "value") else str(deal_stage)
        outcome_type_str = outcome_type.value if hasattr(outcome_type, "value") else str(outcome_type)

        tags = [
            f"deal:{deal_id}",
            f"stage:{stage_str.lower()}",
            "type:outcome",
            "type:action",
            f"outcome:{outcome_type_str.lower()}"
        ]
        if company_id:
            tags.append(f"company:{company_id}")

        try:
            logger.info(f"Hindsight outcome retain started | bank_id={self.bank_id} | deal_id={deal_id}")
            if hasattr(client, "aretain"):
                res = client.aretain(
                    bank_id=self.bank_id,
                    content=content,
                    context=f"deal:{deal_id}",
                    metadata={
                        "deal_id": deal_id,
                        "company": company_name,
                        "stage": stage_str,
                        "outcome_type": outcome_type_str,
                        "recommendation_title": recommendation_title
                    },
                    tags=tags
                )
                if inspect.isawaitable(res):
                    res = await res
            else:
                res = client.retain(
                    bank_id=self.bank_id,
                    content=content,
                    context=f"deal:{deal_id}",
                    metadata={
                        "deal_id": deal_id,
                        "company": company_name,
                        "stage": stage_str,
                        "outcome_type": outcome_type_str,
                        "recommendation_title": recommendation_title
                    },
                    tags=tags
                )
            logger.info(f"Hindsight outcome retain succeeded | bank_id={self.bank_id}")
            memory_id = getattr(res, "id", None) or "retained"
            return HindsightMemoryStatus(
                status="stored",
                bank_id=self.bank_id,
                memory_ids=[memory_id]
            )
        except Exception as e:
            logger.error(f"Hindsight outcome retain failed for deal_id={deal_id}: {str(e)}")
            return HindsightMemoryStatus(
                status="error",
                bank_id=self.bank_id,
                message=f"Memory storage failed: {str(e)}"
            )

    async def recall_memories(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        top_k: int = 10
    ) -> Dict[str, Any]:
        status = await self.get_status()
        if status == HindsightStatus.NOT_CONFIGURED:
            logger.info("Hindsight not configured. RECALL operation skipped.")
            return {
                "status": "not_configured",
                "bank_id": self.bank_id,
                "query": query,
                "results": [],
                "message": "Connect Hindsight memory to analyze historical experiences."
            }
        elif status == HindsightStatus.UNAVAILABLE:
            logger.warning("Hindsight Cloud service unavailable during recall operation.")
            return {
                "status": "unavailable",
                "bank_id": self.bank_id,
                "query": query,
                "results": [],
                "message": "Historical memory unavailable."
            }

        client = get_hindsight_client()
        if not client:
            return {
                "status": "not_configured",
                "bank_id": self.bank_id,
                "query": query,
                "results": [],
                "message": "Hindsight client instance not available."
            }

        await self.ensure_bank_exists()

        try:
            logger.info(f"Hindsight recall started | bank_id={self.bank_id} | query='{query[:60]}...'")
            
            if hasattr(client, "arecall"):
                recall_response = client.arecall(
                    bank_id=self.bank_id,
                    query=query,
                    tags=tags,
                    max_tokens=4096
                )
                if inspect.isawaitable(recall_response):
                    recall_response = await recall_response
            else:
                recall_response = client.recall(
                    bank_id=self.bank_id,
                    query=query,
                    tags=tags,
                    max_tokens=4096
                )
            
            raw_results = getattr(recall_response, "results", []) or []
            parsed_results = []

            for r in raw_results:
                parsed_results.append({
                    "id": getattr(r, "id", None) or "",
                    "content": getattr(r, "text", "") or getattr(r, "content", "") or str(r),
                    "type": getattr(r, "type", None) or "GENERAL_EXPERIENCE",
                    "context": getattr(r, "context", None),
                    "metadata": getattr(r, "metadata", {}) or {},
                    "tags": getattr(r, "tags", []) or [],
                    "document_id": getattr(r, "document_id", None)
                })

            logger.info(f"Hindsight recall succeeded | count={len(parsed_results)}")
            return {
                "status": "success",
                "bank_id": self.bank_id,
                "query": query,
                "results": parsed_results,
                "count": len(parsed_results)
            }
        except Exception as e:
            logger.error(f"Hindsight recall failed: {str(e)}")
            return {
                "status": "error",
                "bank_id": self.bank_id,
                "query": query,
                "results": [],
                "message": f"Historical memory recall failed: {str(e)}"
            }

    async def reflect_memories(
        self,
        query: str,
        context: Optional[str] = None,
        response_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes real Hindsight Cloud REFLECT to synthesize reasoning over recalled evidence.
        """
        status = await self.get_status()
        if status == HindsightStatus.NOT_CONFIGURED:
            logger.info("Hindsight not configured. REFLECT operation skipped.")
            return {
                "status": "not_configured",
                "bank_id": self.bank_id,
                "text": "",
                "structured_output": None,
                "message": "Connect Hindsight memory to run reflect reasoning."
            }
        elif status == HindsightStatus.UNAVAILABLE:
            logger.warning("Hindsight Cloud service unavailable during reflect operation.")
            return {
                "status": "unavailable",
                "bank_id": self.bank_id,
                "text": "",
                "structured_output": None,
                "message": "Historical memory reasoning service unavailable."
            }

        client = get_hindsight_client()
        if not client:
            return {
                "status": "not_configured",
                "bank_id": self.bank_id,
                "text": "",
                "structured_output": None,
                "message": "Hindsight client instance not available."
            }

        await self.ensure_bank_exists()

        try:
            logger.info(f"Hindsight reflect started | bank_id={self.bank_id}")
            if hasattr(client, "areflect"):
                reflect_response = client.areflect(
                    bank_id=self.bank_id,
                    query=query,
                    context=context,
                    response_schema=response_schema,
                    budget="mid"
                )
                if inspect.isawaitable(reflect_response):
                    reflect_response = await reflect_response
            else:
                reflect_response = client.reflect(
                    bank_id=self.bank_id,
                    query=query,
                    context=context,
                    response_schema=response_schema,
                    budget="mid"
                )

            text_output = getattr(reflect_response, "text", "") or ""
            struct_output = getattr(reflect_response, "structured_output", None)

            logger.info(f"Hindsight reflect succeeded")
            return {
                "status": "success",
                "bank_id": self.bank_id,
                "text": text_output,
                "structured_output": struct_output
            }
        except Exception as e:
            logger.error(f"Hindsight reflect failed: {str(e)}")
            return {
                "status": "error",
                "bank_id": self.bank_id,
                "text": "",
                "structured_output": None,
                "message": f"Hindsight reflect failed: {str(e)}"
            }


hindsight_service = HindsightService()
