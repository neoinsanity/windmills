WebEmitter.Router.map(function () {
    this.resource('messages', { path: '/'}, function () {
        // additional child routes
        this.route('active');
        this.route('completed');
    });
});

WebEmitter.MessagesRoute = Ember.Route.extend({
    model: function () {
        return this.store.find('message');
    }
});

WebEmitter.MessagesIndexRoute = Ember.Route.extend({
    model: function () {
        return this.modelFor('messages');
    }
});

WebEmitter.MessagesActiveRoute = Ember.Route.extend({
    model: function () {
        return this.store.filter('message', function (message) {
            return !message.get('isSent');
        });
    },
    renderTemplate: function (controller) {
        this.render('messages/index', {controller: controller})
    }
});

WebEmitter.MessagesCompletedRoute = Ember.Route.extend({
    model: function () {
        return this.store.filter('message', function (message) {
            return message.get('isSent');
        });
    },
    renderTemplate: function (controller) {
        this.render('messages/index', {controller: controller})
    }
});