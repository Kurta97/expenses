from django.test import TestCase
from django.urls import reverse
from datetime import date
from .models import Expense, Category
from .reports import summary_per_category
from .forms import ExpenseSearchForm


class ViewsTests(TestCase):
    def setUp(self):
        self.category1 = Category.objects.create(name='Test Category 1')
        self.category2 = Category.objects.create(name='Test Category 2')
        self.category3 = Category.objects.create(name='Test Category 3')

        Expense.objects.create(
            name='Expense 1',
            date=date(2097, 12, 5),
            amount=10,
            category=self.category1
        )

        Expense.objects.create(
            name='Expense 2',
            date=date(1997, 12, 5),
            amount=20,
            category=self.category2
        )

        Expense.objects.create(
            name='Expense 3',
            date=date(1897, 12, 5),
            amount=20,
            category=self.category3
        )

    def test_expense_list_view(self):
        response = self.client.get(reverse('expenses:expense-list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context)
        self.assertIn('total_amount_spent', response.context)
        self.assertIn('form', response.context)
        self.assertIn('summary_per_category', response.context)
        self.assertIn('summary_per_year_month', response.context)
        self.assertQuerysetEqual(
            response.context['object_list'],
            Expense.objects.all(),
        )

    def test_expense_list_view_with_filter_by_name(self):
        data = {'name': 'Expense 3'}
        response = self.client.get(reverse('expenses:expense-list'), data)
        expected_queryset = Expense.objects.filter(name='Expense 3')

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['object_list'],
            expected_queryset,
        )

    def test_expense_list_view_with_filter_by_date_from(self):
        data = {'date_from': date.today()}
        response = self.client.get(reverse('expenses:expense-list'), data)
        expected_queryset = Expense.objects.filter(date__gte=date.today())

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['object_list'],
            expected_queryset,
        )

    def test_expense_list_view_with_filter_by_date_to(self):
        data = {'date_to': date.today()}
        response = self.client.get(reverse('expenses:expense-list'), data)
        expected_queryset = Expense.objects.filter(date__lte=date.today())

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['object_list'],
            expected_queryset,
        )

    def test_expense_list_view_with_filter_by_category(self):
        data = {'category': self.category1.id}
        response = self.client.get(reverse('expenses:expense-list'), data)
        expected_queryset = Expense.objects.filter(category=self.category1.id)

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['object_list'],
            expected_queryset,
        )

    def test_expense_list_view_with_filter_by_categories(self):
        data = {'category': [self.category1.id, self.category2.id]}
        response = self.client.get(reverse('expenses:expense-list'), data)
        expected_queryset = Expense.objects.filter(
            category__in=data['category']
        )

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['object_list'],
            expected_queryset,
        )

    def test_sort_by_category_asc(self):
        response = self.client.get(
            reverse('expenses:expense-list'), {'sort_by': 'category'}
        )
        expected_data = [
            str(expense) for expense in Expense.objects.order_by('name')
        ]

        self.assertQuerysetEqual(
            response.context['object_list'],
            expected_data,
            transform=lambda x: str(x)
        )

    def test_sort_by_category_desc(self):
        response = self.client.get(
            reverse('expenses:expense-list'), {'sort_by': '-category'}
        )
        expected_data = [
            str(expense) for expense in Expense.objects.order_by('-name')
        ]

        self.assertQuerysetEqual(
            response.context['object_list'],
            expected_data,
            transform=lambda x: str(x)
        )

    def test_sort_by_date_asc(self):
        response = self.client.get(
            reverse('expenses:expense-list'), {'sort_by': 'date'}
        )
        expected_data = [
            str(expense) for expense in Expense.objects.order_by('date')
        ]

        self.assertQuerysetEqual(
            response.context['object_list'],
            expected_data,
            transform=lambda x: str(x)
        )

    def test_sort_by_date_desc(self):
        response = self.client.get(
            reverse('expenses:expense-list'), {'sort_by': '-date'}
        )
        expected_data = [
            str(expense) for expense in Expense.objects.order_by('-date')
        ]

        self.assertQuerysetEqual(
            response.context['object_list'],
            expected_data,
            transform=lambda x: str(x)
        )

    def test_category_list_view(self):
        response = self.client.get(reverse('expenses:category-list'))
        expected_queryset = Category.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context)
        self.assertIn('paginator', response.context)
        self.assertIn('page_obj', response.context)
        self.assertIn('is_paginated', response.context)
        self.assertQuerysetEqual(
            response.context['object_list'],
            expected_queryset,
            ordered=False
        )

    def test_summary_per_category(self):
        queryset = Expense.objects.all()
        result = summary_per_category(queryset)
        expected_result = {
            'Test Category 1': 10,
            'Test Category 2': 20,
            'Test Category 3': 20
        }

        self.assertEqual(result, expected_result)

    def test_summary_per_category_empty_queryset(self):
        queryset = Expense.objects.none()
        result = summary_per_category(queryset)

        self.assertEqual(result, {})

    def test_summary_per_category_with_filter(self):
        queryset = Expense.objects.filter(category=self.category1)
        result = summary_per_category(queryset)
        expected_result = {
            'Test Category 1': 10,
        }

        self.assertEqual(result, expected_result)


class ExpenseSearchFormTests(TestCase):
    def setUp(self):
        self.category1 = Category.objects.create(name='Test Category 1')
        self.category2 = Category.objects.create(name='Test Category 2')
        self.category3 = Category.objects.create(name='Test Category 3')

        Expense.objects.create(
            name='Expense 1',
            date=date(2097, 12, 5),
            amount=10,
            category=self.category1
        )

        Expense.objects.create(
            name='Expense 2',
            date=date(1997, 12, 5),
            amount=20,
            category=self.category2
        )

        Expense.objects.create(
            name='Expense 3',
            date=date(1897, 12, 5),
            amount=20,
            category=self.category3
        )

    def test_form_with_valid_data(self):
        form_data = {
            'name': 'Expense 1',
            'date_from': '2097-12-01',
            'date_to': '2097-12-10',
            'category': [self.category1.id]
        }
        form = ExpenseSearchForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_form_with_empty_data(self):
        form_data = {}
        form = ExpenseSearchForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_form_with_invalid_data(self):
        form_data = {
            'name': 'Expense 1',
            'date_from': 'invalid_date',
            'date_to': 'invalid_date',
            'category': 'invalid_category'
        }
        form = ExpenseSearchForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('date_from', form.errors)
        self.assertIn('date_to', form.errors)
        self.assertIn('category', form.errors)

    def test_form_with_valid_category_ids(self):
        form_data = {
            'name': 'Expense 1',
            'date_from': '2097-12-01',
            'date_to': '2097-12-10',
            'category': [self.category1.id, self.category2.id]
        }
        form = ExpenseSearchForm(data=form_data)

        self.assertTrue(form.is_valid())

        selected_categories = Category.objects.filter(
            id__in=form.cleaned_data['category']
        )
        category_ids = list(selected_categories.values_list('id', flat=True))

        self.assertEqual(
            category_ids, [self.category1.id, self.category2.id]
        )

    def test_form_with_invalid_category_ids(self):
        form_data = {
            'name': 'Expense 1',
            'date_from': '2097-12-01',
            'date_to': '2097-12-10',
            'category': [100, 200]
        }
        form = ExpenseSearchForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)
