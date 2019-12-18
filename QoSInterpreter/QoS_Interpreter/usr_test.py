import json

usr = {
    'ServiceType':'VoiceRecording',
    'USRParameters':[
        {
            'name':'Performance',
            'value':'High'
        },
        {
            'name':'Reliability',
            'value':'Medium'
        }
    ],
    'UserContexts':[
        {
            'name':'Location',
            'value':'N1bldg_rm823'
        },
        {
            'name':'Position',
            'value':'(0.9, 0.26)'
        }
    ]
}

print(json.dumps(usr))
