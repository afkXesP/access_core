from authentication.models import AccessRoleRule, BusinessElement


def check_access(user, element_name, method):
    """
    Проверяет доступ пользователя к ресурсу.

    Алгоритм:
        1. Получить роль пользователя
        2. Найти правило AccessRoleRule
        3. Проверить permission в зависимости от HTTP метода

    Возвращает:
        True - доступ разрешен
        False - доступ запрещен
    """
    if not user or not user.is_authenticated or not user.role:
        return False

    rule = AccessRoleRule.objects.filter(role=user.role, element__name=element_name).first()
    if not rule:
        return False

    match method:
        case "GET":
            return rule.read_permission or rule.read_all_permission

        case "POST":
            return rule.create_permission

        case "PUT" | "PATCH":
            return rule.update_permission or rule.update_all_permission

        case "DELETE":
            return rule.delete_permission or rule.delete_all_permission

    return False
