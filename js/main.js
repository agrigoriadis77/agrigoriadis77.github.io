function getOnload(selectedClass) {
    return function(e) {
        let rows;
        if (e) {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, {type: 'array'});
            const sheet = workbook.Sheets[workbook.SheetNames[0]];
            rows = XLSX.utils.sheet_to_json(sheet, {header: 1});
        } else {
            rows = defaultData;
        }

        const table = Array.from({length: 7}, () => Array(5).fill(''));
        let currentDay = -1;
        let currentHour = -1;

        const maxCols = rows.reduce((max, row) => Math.max(max, row.length), 0);

        for (let col = 0; col < maxCols; col++) {
            for (let row = 0; row < rows.length; row++) {
                const cellValue = (rows[row][col] || '').toString().trim();
                
                switch (cellValue) {
                    case 'ΔΕΥΤΕΡΑ': currentDay = 0; break;
                    case 'ΤΡΙΤΗ': currentDay = 1; break;
                    case 'ΤΕΤΑΡΤΗ': currentDay = 2; break;
                    case 'ΠΕΜΠΤΗ': currentDay = 3; break;
                    case 'ΠΑΡΑΣΚΕΥΗ': currentDay = 4; break;
                    case '1η': currentHour = 0; break;
                    case '2η': currentHour = 1; break;
                    case '3η': currentHour = 2; break;
                    case '4η': currentHour = 3; break;
                    case '5η': currentHour = 4; break;
                    case '6η': currentHour = 5; break;
                    case '7η': currentHour = 6; break;
                    default:
                        if (currentDay !== -1 && currentHour !== -1) {
                            const greekA = 'Α';
                            const classPrefix = selectedClass.startsWith('A') ? 
                                [selectedClass, greekA + selectedClass.slice(1)] : 
                                [selectedClass];

                            if (classPrefix.some(prefix => cellValue.startsWith(prefix))) {
                                const processedValue = processCellValue(cellValue, classPrefix);
                                if (table[currentHour][currentDay]) {
                                    table[currentHour][currentDay] += '\n' + processedValue;
                                } else {
                                    table[currentHour][currentDay] = processedValue;
                                }
                            }
                        }
                }
            }
        }

        displaySchedule(table);
    };
}

function convert(first = false) {
    const fileInput = document.getElementById('fileInput');
    const classroomSelect = document.getElementById('classroomSelect');
    const selectedClass = classroomSelect.value;
    const file = fileInput.files[0];

    if (!file) {
        first = true;
    }

    if (!first) {
        const reader = new FileReader();
        reader.onload = getOnload(selectedClass);
        reader.readAsArrayBuffer(file);
    } else {
        getOnload(selectedClass)(false);
    }
}

function processCellValue(value, prefixes) {
    const tokens = value.split(' ');
    if (tokens.length > 2) {
        tokens[1] = tokens.slice(1).join('');
        tokens.length = 2;
    }
    return tokens
        .filter(token => !prefixes.some(prefix => token.startsWith(prefix)))
        .map(token => replacements[token] || token)
        .join(' ');
}
function displaySchedule(table) {
    const days = ['ΔΕΥΤΕΡΑ', 'ΤΡΙΤΗ', 'ΤΕΤΑΡΤΗ', 'ΠΕΜΠΤΗ', 'ΠΑΡΑΣΚΕΥΗ'];
    let html = '<table class="schedule-table"><thead><tr><th>Ώρα</th>';

    days.forEach(day => html += `<th>${day}</th>`);
    html += '</tr></thead><tbody>';

    for (let hour = 0; hour < 7; hour++) {
        html += `<tr><td>${hour + 1}η</td>`;
        for (let day = 0; day < 5; day++) {
            const cellContent = table[hour][day];
            const bgImage = getBackgroundImage(cellContent);
            const bgClass = bgImage ? 'has-bg-image' : '';
            const bgStyle = bgImage ? `style="background-image: url('css/images/${bgImage}')"` : '';
            //const bgStyle = bgImage ? `style="background-image: url('/images/${bgImage}')"` : '';
            html += `<td class="${bgClass}" ${bgStyle}><span>${cellContent.replace(/\n/g, '<br>')}</span></td>`;
        }
        html += '</tr>';
    }

    html += '</tbody></table>';
    document.getElementById('schedule').innerHTML = html;
}

function getBackgroundImage(subject) {
    if (!subject) return null;
    
    for (const [key, image] of Object.entries(backgroundImages)) {
        if (subject.includes(key)) {
            return image;
        }
    }
    return null;
}

function addEmoji(subject) {
    const emojiMap = {
        'Μαθηματικά': '🔢',
        'Γλώσσα': '📚',
        'Αγγλικά': '🌍',
        'Γυμναστική': '⚽',
        'Μουσική': '🎵',
        'Εικαστικά': '🎨',
        'Ιστορία': '📜',
        'Γεωγραφία': '🗺️',
        'Φυσική': '🔬',
        'Βιολογία': '🧬',
        'Πληροφορική': '💻',
    };

    for (const [key, emoji] of Object.entries(emojiMap)) {
        if (subject.includes(key)) {
            return `${emoji} ${subject}`;
        }
    }
    return subject;
} 