from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
import plotly.graph_objects as go
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
import plotly.graph_objects as go
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/api", tags=["Company Funnel"])

@router.get("/company-funnel", response_class=HTMLResponse)
def company_funnel(
    company_name: str = Query(..., description="Nombre de la compañía"), 
    db: Session = Depends(get_db)
):
    """
    Genera un gráfico de embudo (funnel) con los niveles jerárquicos de una compañía.
    """
    try:
        print(f"📊 Generando funnel para: {company_name}")
        
        # Usar text() y parámetros para prevenir SQL injection
        query = text("""
            SELECT
                COUNT(CASE WHEN jp.level = 'C-Suite' THEN jpcl.id_job END) AS c_suite,
                COUNT(CASE WHEN jp.level = 'VP' THEN jpcl.id_job END) AS vp,
                COUNT(CASE WHEN jp.level = 'Director' THEN jpcl.id_job END) AS director,
                COUNT(CASE WHEN jp.level = 'Manager' THEN jpcl.id_job END) AS manager,
                COUNT(CASE WHEN jp.level = 'Other' THEN jpcl.id_job END) AS other
            FROM companies c
            LEFT JOIN job_positions_company_location jpcl ON c.id_company = jpcl.id_company
            LEFT JOIN job_positions jp ON jpcl.id_job = jp.id_job
            WHERE c.company_name = :company_name
            GROUP BY c.company_name
        """)
        
        result = db.execute(query, {"company_name": company_name}).fetchone()
        
        if not result:
            return HTMLResponse(
                f"<div style='padding:20px;text-align:center;font-family:Inter,sans-serif'>"
                f"<h3>No se encontraron datos para '{company_name}'</h3>"
                f"</div>"
            )
        
        values = [
            result.c_suite,
            result.vp,
            result.director,
            result.manager,
            result.other
        ]
        
        levels = ['C-Suite', 'VP', 'Director', 'Manager', 'Other']
        total = sum(values)
        
        # Si no hay datos, mostrar mensaje
        if total == 0:
            return HTMLResponse(
                f"<div style='padding:20px;text-align:center;font-family:Inter,sans-serif'>"
                f"<h3>No hay headcount registrado para '{company_name}'</h3>"
                f"</div>"
            )
        
        max_val = max(values)
        offsets = [(max_val - v) / 2 for v in values]
        colors = ['#4caf50', '#607d8b', '#607d8b', '#607d8b', '#607d8b']
        
        # Crear figura de Plotly
        fig = go.Figure()
        
        # Barras invisibles para offset (centrado)
        fig.add_trace(go.Bar(
            y=levels,
            x=offsets,
            orientation='h',
            marker_color='rgba(0,0,0,0)',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Barras visibles con headcount
        fig.add_trace(go.Bar(
            y=levels,
            x=values,
            orientation='h',
            marker_color=colors,
            text=[f"{v} HC ({v/total*100:.1f}%)" if v > 0 else "" for v in values],
            textposition='inside',
            textfont=dict(color='white', size=12),
            hovertemplate='<b>%{y}</b><br>Headcount: %{x}<extra></extra>'
        ))
        
        # Layout
        fig.update_layout(
            title=f"Organizational Levels - {company_name}",
            barmode='stack',
            xaxis=dict(showticklabels=False, showgrid=False),
            yaxis=dict(autorange='reversed', showgrid=False),
            height=450,
            margin=dict(l=120, r=50, t=80, b=50),
            font=dict(family="'Inter','Montserrat',sans-serif", size=13),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        
        print(f"✅ Funnel generado: Total HC = {total}")
        
        # Devolver gráfico como HTML embebido
        html_content = fig.to_html(
            full_html=False,
            include_plotlyjs='cdn',
            config={'displayModeBar': False}
        )
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        print(f"❌ Error generando funnel: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))