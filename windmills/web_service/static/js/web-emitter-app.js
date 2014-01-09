window.WebEmitter = Ember.Application.create();

WebEmitter.Store = DS.Store.extend({
    revision: 13,
    adapter: DS.FixtureAdapter
});

WebEmitter.MessagesController = Ember.ArrayController.extend({
    actions: {
        createMessage: function () {
            // get the message body set by the "New Message" text field
            var body = this.get('newMessage');
            if (!body.trim()) {
                return;
            }

            // create the new Message model
            var message = this.store.createRecord('message', {
                body: body,
                isSent: false,
            });

            // clear the "New Message" text field
            this.set('newMessage', '');

            // save the new modal
            message.save();
        }
    }
});