WebEmitter.Message = DS.Model.extend({
    body: DS.attr('string'),
    isSent: DS.attr('boolean')
});
