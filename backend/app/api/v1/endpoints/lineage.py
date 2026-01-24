from fastapi import APIRouter, HTTPException
from backend.app.services.graph_service import graph_service

router = APIRouter()


@router.get("/lineage")
def get_lineage(limit: int = 100):
    """
    Get graph data for visualization.
    Returns nodes and links in a format suitable for force-graph.
    """
    try:
        # Fetch relationships and connected nodes with explicit property return
        # keys need to be explicit because langchain .query() returns dicts of properties for nodes
        query = f"""
        MATCH (n)-[r]->(m)
        RETURN 
            elementId(n) as n_id, 
            labels(n) as n_labels, 
            n as n_props,
            elementId(m) as m_id, 
            labels(m) as m_labels, 
            m as m_props,
            type(r) as r_type,
            elementId(r) as r_id
        LIMIT {limit}
        """
        results = graph_service.execute_cypher(query)

        nodes = {}
        links = []

        # Properties to exclude from frontend (large/internal)
        EXCLUDED_PROPS = {"embedding"}

        def filter_props(props: dict) -> dict:
            return {k: v for k, v in props.items() if k not in EXCLUDED_PROPS}

        for record in results:
            # Process source node
            n_id = record["n_id"]
            n_props = record["n_props"]
            n_labels = record["n_labels"]
            n_group = n_labels[0] if n_labels else "Unknown"

            # Smart label detecion
            n_label = n_props.get("name", n_props.get("title", n_group))

            if n_id not in nodes:
                nodes[n_id] = {
                    "id": n_id,
                    "label": n_label,
                    "group": n_group,
                    "properties": filter_props(n_props),
                }

            # Process target node
            m_id = record["m_id"]
            m_props = record["m_props"]
            m_labels = record["m_labels"]
            m_group = m_labels[0] if m_labels else "Unknown"

            m_label = m_props.get("name", m_props.get("title", m_group))

            if m_id not in nodes:
                nodes[m_id] = {
                    "id": m_id,
                    "label": m_label,
                    "group": m_group,
                    "properties": filter_props(m_props),
                }

            # Process relationship
            links.append(
                {
                    "source": n_id,
                    "target": m_id,
                    "type": record["r_type"],
                    "label": record["r_type"],
                }
            )

        return {"nodes": list(nodes.values()), "links": links}

    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error in lineage endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
