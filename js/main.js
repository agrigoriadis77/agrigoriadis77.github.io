let debug = false;

function generateClassPrefixes(selectedClass) {
    if (!selectedClass || selectedClass.length < 2) return [selectedClass];
    const num = selectedClass.slice(1);
    const first = selectedClass.charAt(0).toUpperCase();

    if (["A", "Α"].includes(first)) {
        // include both Latin A and Greek Alpha
        return ["A" + num, "Α" + num];
    } else if (["B", "Β"].includes(first)) {
        // include both Latin B and Greek Beta
        return ["B" + num, "Β" + num];
    } else if (first === "Γ") {
        // Gamma is only in Greek per requirement
        return ["Γ" + num];
    }

    return [selectedClass];
}

function getOnload(selectedClass) {
    return function (e) {
        let rows;
        if (e) {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, {type: 'array'});
            const sheet = workbook.Sheets[workbook.SheetNames[0]];
            rows = XLSX.utils.sheet_to_json(sheet, {header: 1});
        } else {
            rows = defaultData;
        }

        const table = Array.from({length: 7}, () => Array.from({length: 5}, () => []));
        let currentDay = -1;
        let currentHour = -1;

        const maxCols = rows.reduce((max, row) => Math.max(max, row.length), 0);

        // to get the new defaultData object, put a breakpoint here and get
        // copy(rows.slice(0, rows)) and this will save it to clipboard

        debugger;

        for (let col = 0; col < maxCols; col++) {
            for (let row = 0; row < rows.length; row++) {
                const cellValue = (rows[row][col] || '').toString().trim();
                if (debug) console.log('current day hour:', currentDay, currentHour, 'cellValue:', cellValue);
                switch (cellValue) {
                    case 'ΔΕΥΤΕΡΑ':
                        currentDay = 0;
                        break;
                    case 'ΤΡΙΤΗ':
                        currentDay = 1;
                        break;
                    case 'ΤΕΤΑΡΤΗ':
                        currentDay = 2;
                        break;
                    case 'ΠΕΜΠΤΗ':
                        currentDay = 3;
                        break;
                    case 'ΠΑΡΑΣΚΕΥΗ':
                        currentDay = 4;
                        break;
                    case '1η':
                        currentHour = 0;
                        break;
                    case '2η':
                        currentHour = 1;
                        break;
                    case '3η':
                        currentHour = 2;
                        break;
                    case '4η':
                        currentHour = 3;
                        break;
                    case '5η':
                        currentHour = 4;
                        break;
                    case '6η':
                        currentHour = 5;
                        break;
                    case '7η':
                        currentHour = 6;
                        break;
                    default:
                        if (currentDay !== -1 && currentHour !== -1) {
                            // build class prefixes depending on selectedClass
                            const classPrefix = generateClassPrefixes(selectedClass);  // B2 B2
                            const cellValueUpper = cellValue.toUpperCase(); // B2 \N GL'W
                            if (classPrefix.some(prefix => cellValueUpper.startsWith(prefix.toUpperCase()))) { // psaxnw keli poy na ksekinaei me to onoma ths takshs
                                const processedValue = processCellValue(cellValue, classPrefix).trim();
                                if (!table[currentHour][currentDay].includes(processedValue)) {
                                    let element = table[currentHour][currentDay];
                                    if (debug) element.push(cellValue);
                                    element.push(processedValue);
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
    const selectedClass = classroomSelect.value.trim().toUpperCase();
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
    const tokens = value.split(/[\s\n]+/);
    if (tokens.length > 2) {
        tokens[1] = tokens.slice(1).join('');
        tokens.length = 2;
    }
    if (debug) console.log('Tokens:', tokens);
    let s = tokens
        .filter(token => {  // remove class tokens
            const tokenUpper = token.toUpperCase();
            return !prefixes.some(prefix => tokenUpper.startsWith(prefix.toUpperCase()));
        })
        .map(token => {  // work on the other tokens which are lessons
            for (const [pattern, replacement] of Object.entries(replacements)) {
                const re = pattern instanceof RegExp ? pattern : new RegExp(pattern, 'iu');
                if (re.test(token)) return token.replace(re, replacement);
            }
            return token;
        })
        .join(' ')

    if (debug) console.log('After replacements:', s);
    return s;
}

function displaySchedule(table) {
    const days = ['ΔΕΥΤΕΡΑ', 'ΤΡΙΤΗ', 'ΤΕΤΑΡΤΗ', 'ΠΕΜΠΤΗ', 'ΠΑΡΑΣΚΕΥΗ'];
    let html = '<table class="schedule-table"><thead><tr>';
    html += '<th>Ώρα</th>';
    days.forEach(day => html += `<th>${day}</th>`);
    html += '</tr></thead><tbody>';

    for (let hour = 0; hour < 7; hour++) {
        html += `<tr><td>${hour + 1}η</td>`;
        for (let day = 0; day < 5; day++) {
            const cellContent = table[hour][day];
            const bgImage = getBackgroundImage(cellContent);
            const bgClass = bgImage ? 'has-bg-image' : '';
            const bgStyle = bgImage ? `style="background-image: url('css/images/${bgImage}')"` : '';
            const lessonList = cellContent.length > 0 ? cellContent.join('<br>') : '';
            html += `<td class="${bgClass}" ${bgStyle}><span>${lessonList}</span></td>`;
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

/*function addEmoji(subject) {
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
}*/

if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        try {
            convert(true);
        } catch (err) {
            console.error('Error initializing schedule on DOMContentLoaded:', err);
        }
    });
}
