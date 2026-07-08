// All Helltide marker positions extracted directly from helltides.com source.
// Coordinates are in absolute pixels matching each zone's map image dimensions.
// Coordinate system: lat = Y from top, lng = X from left.

const MAP_DATA = {
  "fractured-peaks": {
    label: "Fractured Peaks",
    imgUrl: "https://helltides.com/images/map/fractured_peaks.png",
    width: 1687, height: 1038,
    markers: {
      mystery: [
        { lat:458, lng:897.5, label:"Olyam Tundra" },
        { lat:764.5, lng:450.7, label:"Western Ways" },
        { lat:253, lng:1009, label:"Kor Rohavan" },
        { lat:715.5, lng:383.5, label:"Western Ways" },
      ],
      hellwyrms: [
        {lat:314,lng:1102},{lat:425,lng:1131},{lat:392,lng:1077},{lat:401,lng:876},
        {lat:450,lng:877},{lat:468,lng:884},{lat:470,lng:935},{lat:515,lng:953},
        {lat:233,lng:1329},{lat:190,lng:1259},{lat:181,lng:1196},{lat:190,lng:1151},
        {lat:208,lng:1003},{lat:327,lng:886},{lat:488,lng:665},{lat:433,lng:530},
        {lat:553,lng:567},{lat:497,lng:715},{lat:623,lng:973},{lat:695,lng:955},
        {lat:738,lng:788},{lat:629,lng:765},{lat:623,lng:733},{lat:713,lng:530},
        {lat:751,lng:421},{lat:798,lng:339},{lat:830,lng:388},{lat:215,lng:1196},
        {lat:479,lng:962},{lat:722,lng:955},{lat:722,lng:1128},{lat:624,lng:1039},
        {lat:573,lng:973},{lat:487,lng:1089},{lat:233,lng:1362},{lat:233,lng:1133},
        {lat:233,lng:1077},{lat:242,lng:994},{lat:215,lng:944},{lat:282,lng:890},
        {lat:479,lng:1137}
      ].map(p => ({...p, label:"Hellwyrm"})),
      events: [
        {lat:708,lng:468},{lat:674,lng:752},{lat:393,lng:539},{lat:470,lng:723},
        {lat:700,lng:1059},{lat:459,lng:1082},{lat:227,lng:1008},{lat:184,lng:1388}
      ].map(p => ({...p, label:"Event"})),
      rituals: [
        { lat:591, lng:696, label:"Accursed Ritual" },
        { lat:548, lng:997, label:"Accursed Ritual" }
      ],
      kixxarth: []
    }
  },
  "hawezar": {
    label: "Hawezar",
    imgUrl: "https://helltides.com/images/map/hawezar.png",
    width: 1354, height: 793,
    markers: {
      mystery: [
        { lat:610, lng:455.5, label:"Pilgram's Cave" },
        { lat:67, lng:451.5, label:"Plains of Attrition" },
        { lat:285.4, lng:603.6, label:"The Devouring Moon" },
        { lat:744.9, lng:741.1, label:"Intruder's Claim" },
      ],
      hellwyrms: [
        {lat:680,lng:641},{lat:713,lng:717},{lat:671,lng:798},{lat:632,lng:756},
        {lat:462,lng:582},{lat:484,lng:606},{lat:475,lng:662},{lat:629,lng:671},
        {lat:647,lng:647},{lat:681,lng:682},{lat:632,lng:723},{lat:548,lng:606},
        {lat:563,lng:563},{lat:596,lng:476},{lat:605,lng:529},{lat:655,lng:554},
        {lat:619,lng:558},{lat:44,lng:509},{lat:60,lng:454},{lat:496,lng:747},
        {lat:525,lng:677},{lat:520,lng:633},{lat:614,lng:818},{lat:306,lng:548},
        {lat:149,lng:448},{lat:137,lng:476},{lat:171,lng:515},{lat:282,lng:650},
        {lat:379,lng:615},{lat:361,lng:536},{lat:320,lng:506},{lat:223,lng:506},
        {lat:253,lng:511},{lat:248,lng:711},{lat:320,lng:726},{lat:291,lng:612},
        {lat:596,lng:439},{lat:647,lng:488},{lat:560,lng:702},{lat:545,lng:741},
        {lat:528,lng:774},{lat:572,lng:780},{lat:578,lng:823},{lat:546,lng:823}
      ].map(p => ({...p, label:"Hellwyrm"})),
      events: [
        {lat:663,lng:695},{lat:557,lng:526},{lat:525,lng:705},{lat:345,lng:625},
        {lat:274,lng:556},{lat:235,lng:645},{lat:150,lng:512}
      ].map(p => ({...p, label:"Event"})),
      rituals: [
        { lat:319, lng:698, label:"Accursed Ritual" },
        { lat:674, lng:749, label:"Accursed Ritual" }
      ],
      kixxarth: []
    }
  },
  "scosglen": {
    label: "Scosglen",
    imgUrl: "https://helltides.com/images/map/scosglen.png",
    width: 1544, height: 878,
    markers: {
      mystery: [
        { lat:667.75, lng:962.0, label:"Fothrach Castle" },
        { lat:81, lng:711.2, label:"Issalia's Rise" },
        { lat:611.5, lng:1009.2, label:"Stormbreak Cove" },
        { lat:222.25, lng:648.0, label:"The Ancient's Woods" },
        { lat:334.5, lng:695.0, label:"The Dead Barks Wilderness" },
        { lat:220.5, lng:473.5, label:"Vasily's Reach" },
        { lat:454, lng:767.5, label:"Writhing Brook" },
        { lat:621.5, lng:699.0, label:"Abandoned Coast" },
      ],
      hellwyrms: [
        {lat:134,lng:614},{lat:209,lng:632},{lat:116,lng:699},{lat:86,lng:708},
        {lat:297,lng:735},{lat:316,lng:684},{lat:409,lng:681},{lat:369,lng:745},
        {lat:358,lng:768},{lat:178,lng:650},{lat:231,lng:623},{lat:235,lng:641},
        {lat:218,lng:699},{lat:219,lng:539},{lat:210,lng:521},{lat:179,lng:512},
        {lat:625,lng:899},{lat:610,lng:997},{lat:662,lng:992},{lat:687,lng:911},
        {lat:705,lng:884},{lat:592,lng:787},{lat:456,lng:857},{lat:448,lng:823},
        {lat:485,lng:761},{lat:409,lng:777},{lat:693,lng:959},{lat:373,lng:805},
        {lat:566,lng:769},{lat:522,lng:923},{lat:160,lng:690},{lat:142,lng:560},
        {lat:179,lng:548},{lat:116,lng:587},{lat:474,lng:805},{lat:610,lng:959},
        {lat:643,lng:929},{lat:616,lng:726}
      ].map(p => ({...p, label:"Hellwyrm"})),
      events: [
        {lat:706.75,lng:922.05},{lat:656,lng:783},{lat:618,lng:873},{lat:543,lng:912},
        {lat:497,lng:807},{lat:371,lng:699},{lat:203,lng:520},{lat:105,lng:710}
      ].map(p => ({...p, label:"Event"})),
      rituals: [
        { lat:649, lng:879, label:"Accursed Ritual" },
        { lat:194, lng:588, label:"Accursed Ritual" }
      ],
      kixxarth: []
    }
  },
  "dry-steppes": {
    label: "Dry Steppes",
    imgUrl: "https://helltides.com/images/map/dry_steppes.png",
    width: 1455, height: 850,
    markers: {
      mystery: [
        { lat:199.75, lng:418.0, label:"Galtmaa Bushland" },
        { lat:477.25, lng:832.5, label:"Wayfarer's Folly" },
        { lat:118.75, lng:751.8, label:"Desolation's Reach" },
        { lat:645.75, lng:819.0, label:"Crucible of Cinder" },
      ],
      hellwyrms: [
        {lat:301,lng:577},{lat:242,lng:631},{lat:354,lng:559},{lat:307,lng:731},
        {lat:268,lng:753},{lat:182,lng:695},{lat:216,lng:713},{lat:194,lng:461},
        {lat:707,lng:795},{lat:698,lng:850},{lat:527,lng:784},{lat:565,lng:755},
        {lat:628,lng:777},{lat:460,lng:813},{lat:442,lng:649},{lat:446,lng:613},
        {lat:536,lng:744},{lat:277,lng:568},{lat:336,lng:519},{lat:354,lng:497},
        {lat:473,lng:676},{lat:461,lng:624},{lat:711,lng:882},{lat:746,lng:864},
        {lat:677,lng:882},{lat:602,lng:740},{lat:600,lng:820},{lat:464,lng:771},
        {lat:498,lng:722},{lat:154,lng:759},{lat:156,lng:709},{lat:132,lng:658},
        {lat:132,lng:613},{lat:172,lng:510},{lat:185,lng:479},{lat:489,lng:789}
      ].map(p => ({...p, label:"Hellwyrm"})),
      events: [
        {lat:691,lng:885},{lat:632,lng:827},{lat:446,lng:588},{lat:320,lng:686},
        {lat:194,lng:507},{lat:224,lng:603},{lat:368,lng:515}
      ].map(p => ({...p, label:"Event"})),
      rituals: [
        { lat:136, lng:675, label:"Accursed Ritual" },
        { lat:503, lng:748, label:"Accursed Ritual" }
      ],
      kixxarth: []
    }
  },
  "kehjistan": {
    label: "Kehjistan",
    imgUrl: "https://helltides.com/images/map/kehjistan.png",
    width: 1474, height: 1017,
    markers: {
      mystery: [
        { lat:57.5, lng:582.7, label:"Hakan's Oasis" },
        { lat:720.75, lng:423.5, label:"Forgotten Coastline" },
        { lat:649, lng:578.2, label:"Scorching Dunes" },
        { lat:92.75, lng:343.2, label:"Shipwreck Cove" },
        { lat:446.25, lng:432.2, label:"Uldur's Cave" },
        { lat:627, lng:608.0, label:"Scorching Dunes" },
        { lat:630.25, lng:434.5, label:"Dimmed Grotto" },
      ],
      hellwyrms: [
        {lat:348,lng:306},{lat:584,lng:458},{lat:576,lng:387},{lat:558,lng:396},
        {lat:450,lng:306},{lat:480,lng:297},{lat:508,lng:324},{lat:330,lng:352},
        {lat:432,lng:396},{lat:391,lng:474},{lat:312,lng:387},{lat:268,lng:324},
        {lat:238,lng:456},{lat:114,lng:515},{lat:61,lng:585},{lat:268,lng:517},
        {lat:453,lng:515},{lat:471,lng:465},{lat:294,lng:524},{lat:171,lng:551},
        {lat:76,lng:456},{lat:626,lng:720},{lat:602,lng:566},{lat:577,lng:548},
        {lat:650,lng:702},{lat:607,lng:789},{lat:644,lng:859},{lat:615,lng:874},
        {lat:546,lng:788},{lat:694,lng:702},{lat:576,lng:625},{lat:791,lng:551},
        {lat:735,lng:474},{lat:760,lng:482},{lat:754,lng:508},{lat:685,lng:456},
        {lat:707,lng:414},{lat:659,lng:551},{lat:53,lng:352},{lat:427,lng:280},
        {lat:325,lng:434},{lat:277,lng:423},{lat:285,lng:476},{lat:238,lng:602},
        {lat:220,lng:530},{lat:180,lng:578},{lat:123,lng:612},{lat:97,lng:643},
        {lat:79,lng:603},{lat:79,lng:560},{lat:85,lng:517},{lat:259,lng:587}
      ].map(p => ({...p, label:"Hellwyrm"})),
      events: [
        {lat:740,lng:482},{lat:655,lng:533},{lat:777,lng:756},{lat:403,lng:233},
        {lat:390,lng:362},{lat:294,lng:407},{lat:321,lng:455},{lat:89,lng:554},
        {lat:237,lng:562}
      ].map(p => ({...p, label:"Event"})),
      rituals: [
        { lat:256, lng:500, label:"Accursed Ritual" },
        { lat:526, lng:355, label:"Accursed Ritual" },
        { lat:650, lng:504, label:"Accursed Ritual" }
      ],
      kixxarth: []
    }
  },
  "nahantu": {
    label: "Nahantu",
    imgUrl: "https://helltides.com/images/map/nahantu.png",
    width: 1299, height: 866,
    markers: {
      mystery: [
        { lat:170, lng:240, label:"Mystery Chest" },
        { lat:487, lng:295, label:"Mystery Chest" },
        { lat:425, lng:460, label:"Mystery Chest" },
        { lat:603, lng:579, label:"Mystery Chest" },
        { lat:424, lng:738, label:"Mystery Chest" },
        { lat:716, lng:1033, label:"Mystery Chest" },
      ],
      hellwyrms: [
        {lat:303,lng:730},{lat:279,lng:742},{lat:648,lng:1102},{lat:523,lng:990},
        {lat:487,lng:983},{lat:523,lng:477},{lat:620,lng:679},{lat:654,lng:764},
        {lat:666,lng:981},{lat:672,lng:672},{lat:581,lng:402},{lat:550,lng:420},
        {lat:582,lng:617},{lat:606,lng:477},{lat:627,lng:451},{lat:581,lng:1132},
        {lat:645,lng:1161},{lat:734,lng:1170},{lat:636,lng:929},{lat:397,lng:843},
        {lat:352,lng:782},{lat:367,lng:804},{lat:469,lng:773},{lat:489,lng:658},
        {lat:433,lng:605},{lat:406,lng:605},{lat:227,lng:642},{lat:153,lng:446},
        {lat:352,lng:484},{lat:370,lng:493},{lat:395,lng:438},{lat:153,lng:334},
        {lat:236,lng:460},{lat:487,lng:385},{lat:309,lng:352}
      ].map(p => ({...p, label:"Hellwyrm"})),
      events: [
        {lat:218,lng:272},{lat:288,lng:524},{lat:460,lng:365},{lat:592,lng:587},
        {lat:671,lng:755},{lat:480,lng:1013},{lat:378,lng:736},{lat:204,lng:623}
      ].map(p => ({...p, label:"Event"})),
      rituals: [
        { lat:307, lng:392, label:"Accursed Ritual" },
        { lat:462, lng:633, label:"Accursed Ritual" }
      ],
      kixxarth: []
    }
  },
  "skovos": {
    label: "Skovos Isles",
    imgUrl: "https://helltides.com/images/map/skovos.png",
    width: 1786, height: 1110,
    markers: {
      mystery: [
        { lat:806, lng:557, label:"Mystery Chest" },
        { lat:728, lng:514, label:"Mystery Chest" },
        { lat:600, lng:559, label:"Mystery Chest" },
        { lat:485, lng:357, label:"Mystery Chest" },
        { lat:578, lng:486, label:"Mystery Chest" },
        { lat:355, lng:1187, label:"Mystery Chest" },
        { lat:148, lng:1209, label:"Mystery Chest" },
        { lat:363, lng:1435, label:"Mystery Chest" },
      ],
      hellwyrms: [
        {lat:133,lng:1077},{lat:613,lng:927},{lat:564,lng:512},{lat:645,lng:802},
        {lat:546,lng:884},{lat:583,lng:1011},{lat:457,lng:850},{lat:583,lng:700},
        {lat:522,lng:638},{lat:466,lng:670},{lat:227,lng:1174},{lat:521,lng:1272},
        {lat:486,lng:1253},{lat:411,lng:1358},{lat:555,lng:1312},{lat:266,lng:1330},
        {lat:209,lng:1076},{lat:504,lng:453},{lat:457,lng:419},{lat:645,lng:548},
        {lat:757,lng:718},{lat:420,lng:539},{lat:429,lng:512}
      ].map(p => ({...p, label:"Hellwyrm"})),
      events: [
        {lat:135,lng:1152},{lat:371,lng:1265},{lat:568,lng:1236},{lat:443,lng:949},
        {lat:694,lng:891},{lat:530,lng:673},{lat:502,lng:435}
      ].map(p => ({...p, label:"Event"})),
      rituals: [
        { lat:692, lng:547, label:"Accursed Ritual" },
        { lat:155, lng:1251, label:"Accursed Ritual" }
      ],
      kixxarth: []
    }
  }
};
