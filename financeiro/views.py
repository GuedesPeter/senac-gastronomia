# Create your views here.

from django.shortcuts import render
from estoque.models import Alimento
from datetime import datetime
from django.db.models import Sum
from .models import Alimento


# FINACEIRO
def financeiro(request):
    # Obter os parâmetros de filtragem e ordenação da URL
    categoria = request.GET.get('categoria', '')
    validade = request.GET.get('validade', '')
    data_entrada = request.GET.get('data_entrada', '')
    fornecedor = request.GET.get('fornecedor', '')
    marca = request.GET.get('marca', '')
    ordenar_por = request.GET.get('ordenar_por', 'nome')  # Coluna padrão para ordenar

    # Função para converter data no formato brasileiro (dd/mm/aaaa) para formato ISO (aaaa-mm-dd)
    def converter_data(data_brasileira):
        try:
            return datetime.strptime(data_brasileira, '%d/%m/%Y').date()
        except ValueError:
            return None

    # Aplicar filtros
    alimentos = Alimento.objects.all()

    if categoria:
        alimentos = alimentos.filter(categoria_nome_icontains=categoria)
    if validade:
        validade_convertida = converter_data(validade)
        if validade_convertida:
            alimentos = alimentos.filter(validade=validade_convertida)
    if data_entrada:
        data_entrada_convertida = converter_data(data_entrada)
        if data_entrada_convertida:
            alimentos = alimentos.filter(data_entrada=data_entrada_convertida)
    if fornecedor:
        alimentos = alimentos.filter(nome_fornecedor__icontains=fornecedor)
    if marca:
        alimentos = alimentos.filter(marca__icontains=marca)

    # Ordenar alimentos
    alimentos = alimentos.order_by(ordenar_por)

    # Calcular métricas
    # Resultado de quantidade por linha
    # quantidade_total = alimentos.count()
   
    # Resultado de quantidade por total
    quantidade_total = sum([alimento.quantidade for alimento in alimentos])
    custo_total = sum([alimento.valor * alimento.quantidade for alimento in alimentos])

    # Contexto para o template
    context = {
        'alimentos': alimentos,
        'quantidade_total': quantidade_total,
        'custo_total': custo_total,
        'categoria': categoria,
        'validade': validade,
        'data_entrada': data_entrada,
        'fornecedor': fornecedor,
        'marca': marca,
        'ordenar_por': ordenar_por
    }

    return render(request, 'financeiro/financeiro.html', context)



# DASHBOARD VIEW
def dashboard(request):
    alimentos = Alimento.objects.all()

    # Calcular totais
    quantidade_total = sum([alimento.quantidade for alimento in alimentos])
    custo_total = sum([alimento.valor * alimento.quantidade for alimento in alimentos])

    # Calcular métricas por categoria e fornecedor
    categoria_data = alimentos.values('categoria__nome').annotate(total=Sum('quantidade'))
    fornecedor_data = alimentos.values('nome_fornecedor').annotate(total=Sum('quantidade'))

    # Preparar listas para o contexto
    categoria_labels = [data['categoria__nome'] for data in categoria_data]
    categoria_totals = [data['total'] for data in categoria_data]

    fornecedor_labels = [data['nome_fornecedor'] for data in fornecedor_data]
    fornecedor_totals = [data['total'] for data in fornecedor_data]

    # Contexto para o template
    context = {
        'categoria_labels': categoria_labels,
        'categoria_totals': categoria_totals,
        'fornecedor_labels': fornecedor_labels,
        'fornecedor_totals': fornecedor_totals,
        'quantidade_total': quantidade_total,
        'custo_total': custo_total,
    }

    return render(request, 'financeiro/dashboard.html', context)