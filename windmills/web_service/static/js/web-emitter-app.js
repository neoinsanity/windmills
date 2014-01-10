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

            // ueclear the "New Message" text field
            this.set('newMessage', '');

            // save the new modal
            message.save();
        }
    },
    remaining: function () {
        return this.filterBy('isSent', false).get('length');
    }.property('@each.isSent'),
    inflection: function () {
        var remaining = this.get('remaining');
        return remaining === 1 ? 'message' : 'messages';
    }.property('remaining')
});

WebEmitter.MessageController = Ember.ObjectController.extend({
    actions: {
        editMessage: function () {
            this.set('isEditing', true);
        }
    },

    isEditing: false,

    isSent: function (key, value) {
        var model = this.get('model');

        if (value === undefined) {
            // property being used as a getter
            return model.get('isSent');
        } else {
            model.set('isSent', value);
            model.save();
            return value;
        }
    }.property('model.isSent')
});