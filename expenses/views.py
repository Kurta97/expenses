from django.db.models import Sum, Count
from django.db.models.functions import ExtractYear, ExtractMonth
from django.views.generic.list import ListView

from .models import Expense, Category
from .forms import ExpenseSearchForm
from .reports import summary_per_category


class ExpenseListView(ListView):
    model = Expense
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        total_amount_spent = queryset.aggregate(total=Sum('amount'))['total']
        form = ExpenseSearchForm(self.request.GET)

        if form.is_valid():
            queryset = self.apply_filters(queryset, form.cleaned_data)
            queryset = self.apply_sorting(
                queryset, self.request.GET.get('sort_by', '')
            )

        summary_per_year_month = self.calculate_summary_per_year_month(queryset)

        return super().get_context_data(
            form=form,
            object_list=queryset,
            total_amount_spent=total_amount_spent,
            summary_per_category=summary_per_category(queryset),
            summary_per_year_month=summary_per_year_month,
            **kwargs
        )

    @staticmethod
    def apply_filters(queryset, cleaned_data):
        name = cleaned_data.get('name', '').strip()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        category = cleaned_data.get('category')

        if name:
            queryset = queryset.filter(name__icontains=name)

        if date_from:
            queryset = queryset.filter(date__gte=date_from)

        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        if category:
            queryset = queryset.filter(category__in=category)

        return queryset

    @staticmethod
    def apply_sorting(queryset, sort_by):
        if sort_by == 'category':
            return queryset.order_by('category')

        elif sort_by == '-category':
            return queryset.order_by('-category')

        elif sort_by == 'date':
            return queryset.order_by('date')

        elif sort_by == '-date':
            return queryset.order_by('-date')

        return queryset

    @staticmethod
    def calculate_summary_per_year_month(queryset):
        return (
            queryset
            .annotate(year=ExtractYear('date'), month=ExtractMonth('date'))
            .values('year', 'month')
            .annotate(total=Sum('amount'))
            .order_by('year', 'month')
        )


class CategoryListView(ListView):
    model = Category
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(num_expenses=Count('expense'))

        return queryset
