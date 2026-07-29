function requireAuth(req, res, next) {
  if (!req.session.user) {
    return res.redirect('/auth/login');
  }
  next();
}

function requireRole(role) {
  return function (req, res, next) {
    if (!req.session.user) {
      return res.redirect('/auth/login');
    }
    if (req.session.user.role !== role) {
      return res.redirect('/unauthorized');
    }
    next();
  };
}

module.exports = { requireAuth, requireRole };
