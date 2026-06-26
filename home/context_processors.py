def role_menu(request):
    user_role = None
    menu = {}
    
    if request.user.is_authenticated:
        if hasattr(request.user, 'userprofile'):
            user_role = request.user.userprofile.role
            
            if user_role == 'PROPRIETOR':
                menu = {
                    'Dashboard': '/reports/dashboard/',
                    'Staff & Salaries': '/profile/staff/',
                    'Payroll': '/profile/salaries/',
                    'Patients': '/profile/patients/',
                    'Stock Inventory': '/stock/',
                    'Stock Approvals': '/stock/approvals/',
                    'Service Catalog': '/case/services/catalog/',
                    'Bills': '/bill/',
                    'Expenses': '/bill/expenses/'
                }
            elif user_role == 'DOCTOR':
                menu = {
                    'Dashboard': '/home/',
                    'Appointments': '/appointments/',
                    'Patients': '/profile/patients/',
                    'Active Visits': '/case/',
                    'Stock / Dispense': '/stock/'
                }
            elif user_role == 'ATTENDANT':
                menu = {
                    'Dashboard': '/home/',
                    'Patients': '/profile/patients/',
                    'Appointments': '/appointments/',
                    'Visits & Check-in': '/case/',
                    'Stock / Dispense': '/stock/',
                    'Bills': '/bill/'
                }
        elif request.user.is_superuser:
            user_role = 'SUPERUSER'
            menu = {
                'Dashboard': '/reports/dashboard/',
                'Patients': '/profile/patients/'
            }
            
    return {'menu': menu, 'user_role': user_role}
