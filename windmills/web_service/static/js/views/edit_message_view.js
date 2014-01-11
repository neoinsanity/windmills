
WebEmitter.EditMessageView = Ember.TextField.extend({
   didInsertElement: function () {
    this.$().focus();
}
});

Ember.Handlebars.helper('edit-message', WebEmitter.EditMessageView);
