window.json = {
    "logoPosition": "right",
    "pages": [
        {
            "name": "page1",
            "elements": [
                {
                    "type": "radiogroup",
                    "name": "question1",
                    "title": "Do I have all the emoji/letter combinations I need to decode the word on my own, without any help from my partner?\"",
                    "isRequired": true,
                    "validators": [
                        {
                            "type": "expression",
                            "text": "You only have half of the letters. Collaboration with your partner is essential to decode the entire word.",
                            "expression": "{question1} == 'No'"
                        }
                    ],
                    "choices": [
                        "Yes",
                        "No"
                    ],
                    "otherText": "Other:",
                    "showClearButton": true
                },
                {
                    "type": "radiogroup",
                    "name": "question2",
                    "title": "Is it necessary to communicate with my partner to obtain the other half of the letters needed to decode the word?",
                    "isRequired": true,
                    "validators": [
                        {
                            "type": "expression",
                            "text": "You must chat with your partner to exchange the missing letters and successfully decode the word.",
                            "expression": "{question2} == 'Yes'"
                        }
                    ],
                    "choices": [
                        "Yes",
                        "No"
                    ],
                    "otherText": "Other:",
                    "showClearButton": true
                },
                {
                    "type": "radiogroup",
                    "name": "question3",
                    "title": "Can I proceed to the next stage of the game as soon as I decode the word, without waiting for my partner to also submit the correct word?",
                    "isRequired": true,
                    "validators": [
                        {
                            "type": "expression",
                            "text": "Both you and your partner must submit the correct word before either of you can proceed. Ensure that you both agree on the decoded word.",
                            "expression": "{question3} == 'No'"
                        }
                    ],
                    "choices": [
                        "Yes",
                        "No"
                    ],
                    "showClearButton": true
                },
                {
                    "type": "radiogroup",
                    "name": "question4",
                    "title": "For each new task will you and your partner  receive a new set of letters and corresponding emojis to decode?",
                    "isRequired": true,
                    "validators": [
                        {
                            "type": "expression",
                            "text": "For each task you and your partner will receive a new set of letters and corresponding emojis and a new word to decode.",
                            "expression": "{question4} == 'Yes'"
                        }
                    ],
                    "choices": [
                        "Yes",
                        "No"
                    ],
                    "showClearButton": true
                }
            ]
        }
    ],
    "showProgressBar": 'auto',
    "progressBarType": "questions",
    "showPrevButton": false,
    "questionsOnPageMode": "questionPerPage",
    "title": "Comprehension Questions",
    "showCompletedPage": false,

}