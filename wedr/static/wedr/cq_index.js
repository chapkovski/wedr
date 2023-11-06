const survey = new Survey.Model(json);
survey.onComplete.add((sender, options) => {
    console.log(JSON.stringify(sender.data, null, 3));
    $('#form').submit();
});

$("#surveyElement").Survey({ model: survey });