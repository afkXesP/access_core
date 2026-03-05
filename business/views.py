from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from authentication.permissions import RBACPermission


class OrdersView(APIView):
    permission_classes = [IsAuthenticated, RBACPermission]
    business_element = 'orders'

    def get(self, request):
        return Response({'orders': [
            {'id': 1, 'title': 'Order №1'},
            {'id': 2, 'title': 'Order №2'},
            {'id': 3, 'title': 'Order №3'},
        ]})

    def post(self, request):
        return Response({'message': 'OK - order created'})


class ProductsView(APIView):
    permission_classes = [IsAuthenticated, RBACPermission]
    business_element = 'products'

    def get(self, request):
        return Response({'products': [
            {'id': 1, 'title': 'Product 1'},
            {'id': 2, 'title': 'Product 2'},
            {'id': 3, 'title': 'Product 3'},
        ]})


class ReportsView(APIView):
    permission_classes = [IsAuthenticated, RBACPermission]
    business_element = 'reports'

    def get(self, request):
        return Response({"report": "Confidential analytics data"})