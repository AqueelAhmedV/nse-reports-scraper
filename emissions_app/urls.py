from rest_framework import routers
from .views import EmissionReportViewSet

router = routers.DefaultRouter()
router.register(r'emission-reports', EmissionReportViewSet)

urlpatterns = router.urls