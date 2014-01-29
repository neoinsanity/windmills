window.WebEmitter = Ember.Application.create();

WebEmitter.Store = DS.Store.extend({
    revision: 13,
    adapter: DS.LSAdapter.extend({
        namespace: 'web-emitter-messages'
    })
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
        },
        clearSent: function () {
            var sent = this.filterBy('isSent', true);
            sent.invoke('deleteRecord');
            sent.invoke('save');
        }
    },

    remaining: function () {
        return this.filterBy('isSent', false).get('length');
    }.property('@each.isSent'),

    inflection: function () {
        var remaining = this.get('remaining');
        return remaining === 1 ? 'message' : 'messages';
    }.property('remaining'),

    hasSent: function () {
        return this.get('sent') > 0;
    }.property('sent'),

    sent: function () {
        return this.filterBy('isSent', true).get('length');
    }.property('@each.isSent'),

    allAreDone: function (key, value) {
        if (value === undefined) {
            return this.get('length') && this.isEvery('isSent');
        } else {
            this.setEach('isSent', value);
            this.invoke('save');
            return value;
        }
    }.property('@each.isSent')
});

WebEmitter.MessageController = Ember.ObjectController.extend({
    actions: {
        editMessage: function () {
            this.set('isEditing', true);
        },
        acceptChanges: function () {
            this.set('isEditing', false);

            if (Ember.isEmpty(this.get('model.body'))) {
                this.send('removeMessage');
            } else {
                this.get('model').save();
            }
        },

        sendMessage: function () {
            var model = this.get('model');

            data = model.getProperties('body');
            $.post("/send_message", data);

            model.set('isSent', true);
            model.save();
        },

        resetMessage: function () {
            var model = this.get('model');
            model.set('isSent', false);
            model.save();
        },

        removeMessage: function () {
            var message = this.get('model');
            message.deleteRecord();
            message.save();
        }
    },

    isEditing: false,
});
