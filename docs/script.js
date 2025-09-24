// Global vars
let table;
let lang = 'en';
let labels;
let mappings;

const LANGUAGES = [
    { code: 'en', label: 'English (EN)' },
    { code: 'la', label: 'Latin (LA)' },
    { code: 'sv', label: 'Svenska (SV)' },
    { code: 'de', label: 'Deutsch (DE)' },
    { code: 'fr', label: 'Français (FR)' },
    { code: 'es', label: 'Español (ES)' },
    { code: 'it', label: 'Italiano (IT)' },
    { code: 'pt', label: 'Português (PT)' },
    { code: 'nl', label: 'Nederlands (NL)' },
];

async function main(){
    // Add listener to support table resizing
    window.addEventListener('resize', debounce(() => table.redraw(true)));

    // Dowload buttons
    document.getElementById('download-csv').addEventListener('click', () => table.download('csv', 'data.csv'));
    document.getElementById('download-json').addEventListener('click', () => table.downloadToTab('json', 'data.json'));
    document.getElementById('download-xlsx').addEventListener('click', () => table.download('xlsx', 'data.xlsx'));

    // Language
    initLanguageSelector();

    // Initialize
    await loadLabels();
    await loadMappings();
    await loadTable();
}

// Load labels
async function loadLabels() {
    const response = await fetch('./labels.json', { cache: 'no-store' });
    labels = await response.json();
}

// Load mappings
async function loadMappings() {
    const response = await fetch('./mappings.json', { cache: 'no-store' });
    mappings = await response.json();
}

// Load table
async function loadTable(){
    const tabledata = [];
    for(let m of mappings['mappings']){
        let source = mappings['sources'][m.source];
        let row = {
            fromIcd: m.from_icd,
            fromCode: m.from_code,
            fromLabel: getLabel(m.from_icd, m.from_code, lang),
            toIcd: m.to_icd,
            toCode: m.to_code,
            toLabel: getLabel(m.to_icd, m.to_code, lang),
            source: m.source,
            attributes: m?.attributes
                ? Object.entries(m.attributes)
                    .map(([k, val]) => `${k}=${val}`)
                    .join(', ')
                : '',
            notes: source.notes
        }
        tabledata.push(row);
    }

    table = new Tabulator('#mapping-table', {
        data: tabledata,
        layout: 'fitColumns',
        addRowPos: 'top',
        pagination: 'local',
        paginationSize: 50,
        paginationCounter: 'rows',
        movableColumns: false,
        selectable: true,
        sortMode: 'multi',
        columnDefaults: {
            headerFilter: 'input',
            widthGrow: 0
        },
        columns: [
            {
                title: 'From',
                headerHozAlign: 'center',
                headerSort: false,
                headerFilter: false,
                columns: [
                    {
                        title: 'ICD',
                        field: 'fromIcd',
                        titleDownload: 'fromIcd',
                        headerFilter: 'list',
                        headerFilterFunc: 'in',
                        headerFilterParams: {
                            valuesLookup: true,
                            sortValuesList: 'asc',
                            multiselect: true
                        }
                    },
                    {
                        title: 'Code',
                        field: 'fromCode',
                        titleDownload: 'fromCode',
                        headerFilterFunc: 'starts'
                    },
                    {
                        title: 'Label',
                        field: 'fromLabel',
                        widthGrow: 2,
                        tooltip: (event, cell) => {
                            return cell.getValue()
                        }

                    },
                ]
            },
            {
                title: 'To',
                headerHozAlign: 'center',
                headerSort: false,
                headerFilter: false,
                columns: [
                    {
                        title: 'ICD',
                        field: 'toIcd',
                        titleDownload: 'toIcd',
                        headerFilter: 'list',
                        headerFilterFunc: 'in',
                        headerFilterParams: {
                            valuesLookup: true,
                            sortValuesList: 'asc',
                            multiselect: true
                        }
                    },
                    {
                        title: 'Code',
                        field: 'toCode',
                        titleDownload: 'toCode',
                        headerFilterFunc: 'starts'
                    },
                    {
                        title: 'Label',
                        field: 'toLabel',
                        titleDownload: 'toLabel',
                        widthGrow: 2,
                        tooltip: (event, cell) => {
                            return cell.getValue()
                        }
                    }
                ]
            },
            {
                title: '',
                headerHozAlign: 'center',
                headerSort: false,
                headerFilter: false,
                columns: [
                    {
                        title: 'Source',
                        field: 'source',
                        titleDownload: 'source',
                        widthGrow: 2,
                        headerFilter: 'list',
                        headerFilterFunc: 'in',
                        headerFilterParams: {
                            valuesLookup: true,
                            sortValuesList: 'asc',
                            multiselect: true
                        }
                    },
                    {
                        title: 'Attributes',
                        field: 'attributes',
                        titleDownload: 'attributes',
                        widthGrow: 1
                    },
                    {
                        title: 'Notes',
                        field: 'notes',
                        titleDownload: 'notes',
                        widthGrow: 2,
                        tooltip: (event, cell) => {
                            return cell.getValue()
                        }
                    }
                ]
            }
        ],
        initialSort: [
            { column: 'fromCode', dir: 'asc' },
            { column: 'fromIcd', dir: 'asc' },
            { column: 'toCode', dir: 'asc' },
            { column: 'toIcd', dir: 'asc' }
        ]
    });

    // sync URL
    table.on('tableBuilt', () => {
        applyHeaderFiltersFromURL();
        table.on('dataFiltered', serializeHeaderFiltersToURL);
    });
}

// Get text label for code
function getLabel(icd, code, lang){
    return labels.labels?.[icd]?.[code]?.[lang];
}

// Abbreviate to international ICD standard
function toInternationalICD(icd) {
  const match = icd.match(/^ICD-\d+/i);
  return match ? match[0] : icd;
}

// Debounce function to reduce number of consecutive calls to fn
function debounce(fn, wait = 10) {
    let t;
    return (...args) => {
        const ctx = this;
        clearTimeout(t);
        t = setTimeout(() => fn.apply(ctx, args), wait);
    };
}

// Write filters to URL
function serializeHeaderFiltersToURL() {
    if (!table) return;

    const params = new URLSearchParams();
    
    // capture current header filters
    const headerFilters = table.getHeaderFilters();
    headerFilters.forEach(({ field, value }) => {
        if (value == null) return;
        if (Array.isArray(value) && value.length === 0) return;
        if (!Array.isArray(value) && String(value).trim() === '') return;

        const serialized = Array.isArray(value) ? value.join(',') : String(value);
        params.set(`${field}`, serialized);
    });

    const qs = params.toString();
    const newURL = `${location.pathname}${qs ? '?' + qs : ''}`;
    history.replaceState(null, '', newURL);
}

// Read filters from URL
function applyHeaderFiltersFromURL() {
    if (!table) return;

    const params = new URLSearchParams(window.location.search);
    params.entries().forEach(([field, raw]) => {
        const col = table.getColumn(field);
        if (col === undefined) return;
        const def = col?.getDefinition?.();

        let value = raw;
        if (def?.headerFilter === 'list' && def?.headerFilterParams?.multiselect) {
            value = raw ? raw.split(',') : [];
        }
        table.setHeaderFilterValue(field, value);
    });
}

// Init lanugage selector
function initLanguageSelector() {
    const dropdownBtn = document.getElementById('language-dropdown');
    const menu = document.getElementById('language-menu');

    // Build menu
    menu.innerHTML = '';
    LANGUAGES.forEach(({ code, label }) => {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.className = 'dropdown-item';
        a.href = '#';
        a.dataset.code = code;
        a.textContent = label;
        a.addEventListener('click', (e) => {
            e.preventDefault();
            lang = code;
            dropdownBtn.textContent = label
            loadTable();
        });
        li.appendChild(a);
        menu.appendChild(li);
    });
}

// Run main
main();