from django.urls import path
from .views import  Advance, Billing, Costs, Thirds, Operations, Prodplant,gre,manual

urlpatterns = [    

	path('advance/', Advance.as_view(), name='advance'),    
	path('billing/', Billing.as_view(), name='billing'),  
	path('costs/', Costs.as_view(), name='costs'), 
	path('thirds/', Thirds.as_view(), name='thirds'), 
	path('operations/', Operations.as_view(), name='operations'),    
	path('prodplant/', Prodplant.as_view(), name='prodplant'),
 	path('gre/', gre.as_view(), name='gre'),
  	path('manual/', manual.as_view(), name='manual'),

]