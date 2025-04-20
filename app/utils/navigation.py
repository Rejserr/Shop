from flask import url_for

def get_nav_items(user):
    nav_items = [
        {
            'text': 'Dashboard',
            'icon': 'fas fa-tachometer-alt',
            'url': url_for('main.index'),
            'permissions': ['NAV_DASHBOARD']
        },
        {
            'text': 'Users',
            'icon': 'fas fa-users',
            'url': url_for('users.list'),
            'permissions': ['NAV_USERS']
        },
        {
            'text': 'Branches',
            'icon': 'fas fa-building',
            'url': url_for('branches.index'),
            'permissions': ['NAV_BRANCHES']
        },
        {
            'text': 'Roles',
            'icon': 'fas fa-user-tag',
            'url': url_for('roles.list'),
            'permissions': ['NAV_ROLES']
        },
        {
            'text': 'Reports',
            'icon': 'fas fa-chart-bar',
            'url': url_for('reports.shipment_status'),
            'permissions': ['NAV_REPORTS']
        },
        {
            'text': 'Zaprimanje',
            'icon': 'fas fa-truck-loading',
            'url': url_for('zaprimanje.receiving_menu'),
            'permissions': ['NAV_ZAPRIMANJE']
        },
        {
            'text': 'MSI API',
            'icon': 'fas fa-database',
            'url': url_for('msi_api.index'),
            'permissions': ['NAV_MSI_API']
        }
    ]
    
    if user.is_anonymous:
        return []
        
    if user.role and user.role.role_name == 'Admin':
        return nav_items  # Admin sees all items
        
    return [item for item in nav_items if user.has_permission(item['permissions'][0])]
