from django.db import models

# 1. A Empresa
class Empresa(models.Model):
    nome = models.CharField(max_length=100)
    ramo = models.CharField(max_length=50) # Ex: Ocultismo, Esoterismo

    def __str__(self):
        return self.nome

# 2. Produto
class Produto(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.PositiveIntegerField(default=0)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)

    def __str__(self):
        return self.nome

# 3. Cliente
class Cliente(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14, unique=True)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    data_nascimento = models.DateField()
    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100, default="Nova Porteirinha")
    cep = models.CharField(max_length=9)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome
    
# 4. Sistema de Vendas Atualizado (Com Múltiplos Itens e Pagamento)

class Venda(models.Model):
    PAGAMENTO_CHOICES = [
        ('PIX', 'PIX'),
        ('DINHEIRO', 'Dinheiro'),
        ('CREDITO', 'Cartão de Crédito'),
        ('DEBITO', 'Cartão de Débito'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    data_venda = models.DateTimeField(auto_now_add=True)
    metodo_pagamento = models.CharField(max_length=20, choices=PAGAMENTO_CHOICES, default='PIX')

    def __str__(self):
        return f"Venda #{self.id} - {self.cliente.nome}"

    @property
    def valor_total(self):
        # Soma o subtotal de todos os itens ligados a esta venda
        return sum(item.subtotal for item in self.itens.all())

# 5. Novo Modelo: Itens da Venda (O "Carrinho")
class ItemVenda(models.Model):
    # O related_name='itens' vai nos ajudar a listar tudo no cupom.html depois
    venda = models.ForeignKey(Venda, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    
    # É importante salvar o preço na hora da venda. Assim, se você mudar o valor 
    # do produto amanhã, o cupom de hoje não será alterado retroativamente.
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario