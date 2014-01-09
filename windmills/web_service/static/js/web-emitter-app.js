
window.WebEmitter = Ember.Application.create();

WebEmitter.Store = DS.Store.extend({
   revision: 13,
    adapter: DS.FixtureAdapter
});

// WebEmitter.ApplicationAdaptor = DS.FixtureAdapter.extend();