WebEmitter.Router.map(function () {
    this.resource('messages', { path: '/'});
});

WebEmitter.MessagesRoute = Ember.Route.extend({
   model: function(){
       return this.store.find('message');
   }
});
