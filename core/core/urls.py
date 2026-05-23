from django.contrib import admin
from django.urls import path
from core_loja import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('loja/<int:empresa_id>/', views.dashboard_loja, name='url_da_loja'),
    path('loja/<int:empresa_id>/novo-cliente/', views.cadastrar_item, {'tipo': 'cliente'}, name='novo_cliente'),
    path('loja/<int:empresa_id>/novo-produto/', views.cadastrar_item, {'tipo': 'produto'}, name='novo_produto'),
    path('loja/<int:empresa_id>/nova-venda/', views.cadastrar_item, {'tipo': 'venda'}, name='nova_venda'),
    path('loja/<int:empresa_id>/atualizar-estoque/<int:produto_id>/', views.atualizar_estoque, name='atualizar_estoque'),
    
    # Rota do Cupom de Impressão
    path('loja/<int:empresa_id>/cupom/<int:venda_id>/', views.cupom_venda, name='cupom_venda'),
]

# Isso permite que o Django mostre as fotos dos produtos no modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)