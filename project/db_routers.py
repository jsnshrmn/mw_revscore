class Router:
    route_facts = {"mw_events", "mw_scores"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_facts:
            return "facts"
        # No opinion
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_facts:
            return "facts"
        # No opinion
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label in self.route_facts
            or obj2._meta.app_label in self.route_facts
        ):
            return True
        # No opinion
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_facts:
            return db == "facts"
        # No opinion
        return None
