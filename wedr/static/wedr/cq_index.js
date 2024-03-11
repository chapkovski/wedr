const survey = new Survey.Model(json);
survey.onComplete.add((sender, options) => {
    var surveyData = JSON.stringify(sender.data, null, 3);
    $('#survey_data').val(surveyData);

    $('#form').submit();
});

$("#surveyElement").Survey({model: survey});