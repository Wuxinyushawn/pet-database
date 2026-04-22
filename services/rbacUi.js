export const ROLE_PERMISSIONS = {
  admin: ['applications:create', 'applications:review', 'adoptions:create', 'followups:create', 'audit:read'],
  staff: ['applications:create', 'applications:review', 'adoptions:create', 'followups:create', 'audit:read'],
  volunteer_coordinator: ['followups:create', 'audit:read']
};

export function permissionsForRole(role) {
  return new Set(ROLE_PERMISSIONS[role] || []);
}

export function applyPermissionVisibility({ root = document, permissions }) {
  root.querySelectorAll('[data-perm-view]').forEach((el) => {
    el.classList.toggle('hidden', !permissions.has(el.dataset.permView));
  });
  root.querySelectorAll('[data-perm-action]').forEach((el) => {
    el.classList.toggle('hidden', !permissions.has(el.dataset.permAction));
  });
}
