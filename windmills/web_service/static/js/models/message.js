WebEmitter.Message = DS.Model.extend({
    body: DS.attr('string'),
    isSent: DS.attr('boolean')
});

WebEmitter.Message.FIXTURES = [
    {
        id: 1,
        body: 'Hola',
        isSent: true
    },
    {
        id: 2,
        body: '...',
        isSent: false
    },
    {
        id: 3,
        body: 'testing 1, 2, 3',
        isSent: false
    }
];
