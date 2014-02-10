WebEmitter.Router.map(function () {
    this.resource('messages', { path: '/'}, function () {
        // additional child routes
        this.route('active');
        this.route('completed');
    });
});

WebEmitter.ApplicationRoute = Ember.Route.extend({
   actions: {
       openModal: function(modalName){
           return this.render(modalName, {
               into: 'application',
               outlet: 'modal'
           });
       },

       closeModal: function(){
           return this.disconnectOutlet({
               outlet: 'modal',
               parentView: 'application'
           })
       }
   }
});

WebEmitter.ModalController = Ember.ObjectController.extend({
   actions: {
       close: function(){
           return this.send('closeModal');
       }
   }
});

WebEmitter.ModalDialogComponent = Ember.Component.extend({
   actions: {
       close: function(){
           return this.sendAction();
       }
   }
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
