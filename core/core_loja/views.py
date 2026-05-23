from django.shortcuts import render, get_object_or_404, redirect
from django.forms import inlineformset_factory
from .models import Empresa, Produto, Cliente, Venda, ItemVenda
from .forms import ClienteForm, ProdutoForm, VendaForm, ItemVendaForm

def dashboard_loja(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    produtos = Produto.objects.filter(empresa=empresa)
    return render(request, 'loja.html', {'empresa': empresa, 'produtos': produtos})

def cadastrar_item(request, empresa_id, tipo):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    
    # MUDANÇA AQUI: extra=1 para abrir apenas 1 produto no carrinho por padrão.
    # O botão de '+ Adicionar Artefato' do HTML vai adicionar os outros.
    ItemVendaFormSet = inlineformset_factory(
        Venda, ItemVenda, form=ItemVendaForm, extra=1, can_delete=False
    )
    formset = None

    if tipo == 'cliente':
        form = ClienteForm(request.POST or None)
        titulo = "Novo Praticante"
    elif tipo == 'produto':
        form = ProdutoForm(request.POST or None, request.FILES or None)
        titulo = "Novo Artefato"
    elif tipo == 'venda':
        form = VendaForm(empresa, request.POST or None)
        # Passamos a empresa para os itens filtrarem os produtos corretos
        formset = ItemVendaFormSet(request.POST or None, form_kwargs={'empresa': empresa})
        titulo = "Registrar Nova Venda"

    if request.method == 'POST':
        if tipo == 'venda':
            # Valida o cabeçalho da venda E os itens do carrinho
            if form.is_valid() and formset.is_valid():
                
                # 1. Checa o estoque de TUDO antes de salvar qualquer coisa
                estoque_ok = True
                for item_form in formset:
                    # Verifica se a linha foi preenchida (ignora linhas em branco)
                    if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                        produto = item_form.cleaned_data['produto']
                        quantidade = item_form.cleaned_data['quantidade']
                        if produto.estoque < quantidade:
                            item_form.add_error('quantidade', f'Estoque insuficiente! Apenas {produto.estoque} disponíveis.')
                            estoque_ok = False
                
                # Se algum produto faltar no estoque, devolve pra tela com o erro
                if not estoque_ok:
                    return render(request, 'form_template.html', {
                        'form': form, 'formset': formset, 'empresa': empresa, 'titulo': titulo, 'tipo': tipo
                    })

                # 2. Salva a Venda Principal (Cliente e Forma de Pagamento)
                venda = form.save(commit=False)
                venda.empresa = empresa
                venda.save()

                # 3. Salva os Itens, atrela à venda e dá baixa no estoque
                itens = formset.save(commit=False)
                for item in itens:
                    item.venda = venda
                    item.preco_unitario = item.produto.preco # Congela o preço no valor atual
                    
                    # Dá baixa no estoque
                    item.produto.estoque -= item.quantidade
                    item.produto.save()
                    
                    item.save()
                
                # Redireciona direto para a impressão da nota fiscal
                return redirect('cupom_venda', empresa_id=empresa.id, venda_id=venda.id)

        else:
            # Para cliente e produto, a lógica antiga funciona perfeitamente
            if form.is_valid():
                item = form.save(commit=False)
                item.empresa = empresa
                item.save()
                
                # MUDANÇA AQUI: Rota direta para corrigir o NoReverseMatch
                return redirect(f'/loja/{empresa.id}/')

    return render(request, 'form_template.html', {
        'form': form, 
        'formset': formset, # Enviamos o formset para o HTML
        'empresa': empresa, 
        'titulo': titulo,
        'tipo': tipo
    })

# NOVA TELA: O Cupom Não-Fiscal
def cupom_venda(request, empresa_id, venda_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    venda = get_object_or_404(Venda, id=venda_id, empresa=empresa)
    return render(request, 'cupom.html', {'empresa': empresa, 'venda': venda})

# NOVA TELA: Atualizar Estoque / Editar Produto existente
def atualizar_estoque(request, empresa_id, produto_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    produto = get_object_or_404(Produto, id=produto_id, empresa=empresa)
    
    form = ProdutoForm(request.POST or None, request.FILES or None, instance=produto)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        
        # MUDANÇA AQUI: Rota direta para corrigir o NoReverseMatch
        return redirect(f'/loja/{empresa.id}/')
        
    return render(request, 'form_template.html', {
        'form': form,
        'empresa': empresa,
        'titulo': f"Atualizar Estoque: {produto.nome}",
        'tipo': 'produto'
    })