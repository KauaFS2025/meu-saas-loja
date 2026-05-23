from django.contrib import admin
from .models import Empresa, Produto, Cliente

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ramo')

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'empresa')
    list_filter = ('empresa',)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    # Escolhi os melhores campos para aparecerem na lista do seu mercado místico
    list_display = ('nome', 'cpf', 'telefone', 'cidade', 'empresa', 'ativo')
    list_filter = ('empresa', 'ativo')