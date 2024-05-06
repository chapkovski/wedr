const json = {
    "logoPosition": "right",
    "pages": [
        {
            "name": "page1",
            "elements": [
                {
                    "type": "radiogroup",
                    "name": "women",
                    "choices": [
                        {"value": 0, "text": "Strongly Disagree"},
                        {"value": 1, "text": "Moderately Disagree"},
                        {"value": 2, "text": "Slightly Disagree"},
                        {"value": 3, "text": "Slightly Agree"},
                        {"value": 4, "text": "Moderately Agree"},
                        {"value": 5, "text": "Strongly Agree"}
                    ]
                    ,
                    "title": "Women should have the right to choose to have an abortion.",
                    "isRequired": true
                },
                {
                    "type": "radiogroup",
                    "name": "partisanship",
                    "title": "I identify more with the Democratic party than with the Republican party.",
                    "choices":    [
                        {"value": 0, "text": "Strongly Disagree"},
                        {"value": 1, "text": "Moderately Disagree"},
                        {"value": 2, "text": "Slightly Disagree"},
                        {"value": 3, "text": "Slightly Agree"},
                        {"value": 4, "text": "Moderately Agree"},
                        {"value": 5, "text": "Strongly Agree"}
                    ]
                },
                {
                    "type": "radiogroup",
                    "name": "immigration",
                    "title": "Immigrants today are a burden on our country because they take our jobs, housing and healthcare.",
                     "choices": [
                        {"value": 0, "text": "Strongly Disagree"},
                        {"value": 1, "text": "Moderately Disagree"},
                        {"value": 2, "text": "Slightly Disagree"},
                        {"value": 3, "text": "Slightly Agree"},
                        {"value": 4, "text": "Moderately Agree"},
                        {"value": 5, "text": "Strongly Agree"}
                    ]
                },
                {
                    "type": "radiogroup",
                    "name": "books",
                    "title": "Physical books are preferable to e-books for recreational reading.",
                     "choices": [
                        {"value": 0, "text": "Strongly Disagree"},
                        {"value": 1, "text": "Moderately Disagree"},
                        {"value": 2, "text": "Slightly Disagree"},
                        {"value": 3, "text": "Slightly Agree"},
                        {"value": 4, "text": "Moderately Agree"},
                        {"value": 5, "text": "Strongly Agree"}
                    ]
                },
                {
                    "type": "radiogroup",
                    "name": "cities",
                    "title": "Cities should invest more in parks and green spaces than in large shopping centers.",
                     "choices": [
                        {"value": 0, "text": "Strongly Disagree"},
                        {"value": 1, "text": "Moderately Disagree"},
                        {"value": 2, "text": "Slightly Disagree"},
                        {"value": 3, "text": "Slightly Agree"},
                        {"value": 4, "text": "Moderately Agree"},
                        {"value": 5, "text": "Strongly Agree"}
                    ]
                },
                {
                    "type": "radiogroup",
                    "name": "cars",
                    "title": "In the future, self-driving cars are preferable to human-driven cars.",
                     "choices": [
                        {"value": 0, "text": "Strongly Disagree"},
                        {"value": 1, "text": "Moderately Disagree"},
                        {"value": 2, "text": "Slightly Disagree"},
                        {"value": 3, "text": "Slightly Agree"},
                        {"value": 4, "text": "Moderately Agree"},
                        {"value": 5, "text": "Strongly Agree"}
                    ]
                }
            ],
            "title": "Please indicate the extent to which you agree or disagree with the following statement:",

            "questionsOrder": "random"
        }
    ],
    "questionsOnPageMode": "questionPerPage",
    "showPrevButton": false,
    "completeText": "Next",
    "showCompletedPage": false,
    "showProgressBar": 'auto',
    "progressBarType": "questions",
}