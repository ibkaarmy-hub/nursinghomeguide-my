/**
 * NursingHomeGuide.my — Operator intake form generator
 *
 * ONE-SHOT SCRIPT. Builds the operator verification form (per
 * _research/verification-sop.md §5) with questions across 9 sections
 * (A–I), and links responses to a new tab in the master Sheet.
 *
 * HOW TO USE:
 *   1. Open script.google.com → New project
 *   2. Paste this entire file into the editor (replace the default Code.gs)
 *   3. Click "Save" (floppy icon)
 *   4. From the function dropdown at the top, choose: buildIntakeForm
 *   5. Click "Run". First run prompts for permissions — approve.
 *   6. Open the "Execution log" pane. The form URLs print there.
 *
 * WHAT GETS CREATED:
 *   - A Google Form titled "NursingHomeGuide.my — Operator Verification"
 *   - A new tab on the master Sheet for form responses
 *   - Three URLs in the log: public URL, edit URL, response sheet URL
 *
 * AFTER CREATION:
 *   - Open the public URL once to confirm sections look right
 *   - Use the form's "Get pre-filled link" feature (in Forms UI, top-right
 *     menu) to build per-facility links with name + address pre-filled
 *   - Share pre-filled links with operators via WhatsApp/email per the SOP
 *
 * SAFE TO RE-RUN: each run creates a new form. If you re-run after
 * changes, archive or delete the old form via Drive trash.
 */

const MASTER_SHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk';

function buildIntakeForm() {
  const form = FormApp.create('NursingHomeGuide.my — Operator Verification');
  form.setDescription(
    'Help families find the right care for their loved ones by confirming key facts ' +
    'about your facility. Takes about 5 minutes. Once submitted, your facility profile ' +
    'on NursingHomeGuide.my will display a "Verified — operator-confirmed" badge with ' +
    'today\'s date. We never publish licence numbers or documents you share with us; ' +
    'only the verification status appears publicly.'
  );
  form.setProgressBar(true);
  form.setShowLinkToRespondAgain(false);
  form.setConfirmationMessage(
    'Thank you. We\'ve received your submission and will update your profile within ' +
    'a few working days. If you sent us licence documents, we\'ll review for the ' +
    '"document-verified" badge tier and follow up if anything is unclear.'
  );

  // ─── Section A — Identity ─────────────────────────────────────────
  form.addPageBreakItem()
    .setTitle('A. Facility identity')
    .setHelpText('Confirm your facility\'s identity. The first two fields may be pre-filled if you came here from a NursingHomeGuide.my link.');

  form.addTextItem()
    .setTitle('Facility name')
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('Facility address')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Your name and role at the facility')
    .setHelpText('e.g. "Sarah Tan, Operations Manager"')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Best contact phone or WhatsApp number')
    .setRequired(true);

  // ─── Section B — Licensing ────────────────────────────────────────
  form.addPageBreakItem().setTitle('B. Licensing');

  form.addMultipleChoiceItem()
    .setTitle('What licence does your facility hold?')
    .setChoiceValues([
      'MOH-licensed under Act 586 (Private Healthcare Facilities)',
      'MOH-licensed under Act 802 (Private Aged Healthcare Facilities)',
      'JKM-registered under Act 506 (Pusat Jagaan)',
      'Multiple — I will note details below',
      'None / pending'
    ])
    .showOtherOption(true)
    .setRequired(true);

  form.addTextItem()
    .setTitle('Licence expiry month and year')
    .setHelpText('Format MM/YYYY — e.g. 03/2027');

  form.addMultipleChoiceItem()
    .setTitle('Are you willing to share a copy of your licence with us privately for verification?')
    .setHelpText('Documents stay private and are never republished. Sharing them lets us upgrade your profile to the "document-verified" badge tier.')
    .setChoiceValues(['Yes', 'No', 'Maybe — happy to discuss'])
    .setRequired(true);

  // ─── Section C — Capacity ─────────────────────────────────────────
  form.addPageBreakItem().setTitle('C. Capacity');

  form.addTextItem()
    .setTitle('Total bed count')
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle('Room types offered')
    .setChoiceValues([
      'Dormitory',
      '4-bed',
      'Shared (2-bed)',
      'Single',
      'Single en-suite',
      'Suite'
    ])
    .showOtherOption(true)
    .setRequired(true);

  form.addTextItem()
    .setTitle('Approximate current occupancy (%)')
    .setHelpText('Optional');

  // ─── Section D — Staffing ─────────────────────────────────────────
  form.addPageBreakItem().setTitle('D. Staffing');

  form.addMultipleChoiceItem()
    .setTitle('Is a registered nurse (RN) on duty 24/7?')
    .setChoiceValues([
      'Yes — RN on-site at all times',
      'No — caregiver-led with RN on call',
      'No'
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Person in charge during shifts')
    .setChoiceValues([
      'Registered Nurse',
      'Senior Registered Nurse',
      'Caregiver-supervisor',
      'Other'
    ])
    .showOtherOption(true)
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Doctor visit frequency')
    .setChoiceValues([
      'Daily',
      'Weekly',
      'Fortnightly',
      'Monthly',
      'On-call only'
    ])
    .setRequired(true);

  // ─── Section E — Care capabilities ────────────────────────────────
  form.addPageBreakItem()
    .setTitle('E. Care capabilities')
    .setHelpText('For each capability, indicate whether your facility currently offers it.');

  const capabilities = [
    'Dementia care',
    'Dedicated dementia secure unit (locked / controlled access)',
    'Post-stroke rehabilitation support',
    'Palliative care (symptom management, end-of-life support)',
    'PEG / tube feeding management',
    'Tracheostomy care',
    'Advanced wound care (beyond basic dressings)',
    'On-site physiotherapy',
    'On-site occupational therapy',
    'On-site oxygen therapy',
    'Dialysis support (in-facility or transport arranged)',
    'Medication management (dispensing, monitoring, administration)'
  ];
  capabilities.forEach(cap => {
    form.addMultipleChoiceItem()
      .setTitle(cap)
      .setChoiceValues([
        'Yes — we offer this',
        'No — we do not',
        'Limited — please describe in section I'
      ])
      .setRequired(true);
  });

  // ─── Section F — Pricing ──────────────────────────────────────────
  form.addPageBreakItem().setTitle('F. Pricing');

  form.addMultipleChoiceItem()
    .setTitle('Pricing model')
    .setChoiceValues([
      'All-in monthly fee (everything included)',
      'Base fee + consumables billed separately',
      'Base fee + medical add-ons billed separately',
      'Other'
    ])
    .showOtherOption(true)
    .setRequired(true);

  form.addTextItem()
    .setTitle('Approximate monthly fee range')
    .setHelpText('e.g. "RM 2,800 – RM 4,500 depending on room type"')
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle('What is NOT included in the base fee?')
    .setChoiceValues([
      'Diapers',
      'Milk feeds / formula',
      'Wound dressings',
      'Medication',
      'Doctor visits',
      'Physiotherapy sessions',
      'Transport to appointments',
      'Special diets'
    ])
    .showOtherOption(true);

  // ─── Section G — Service mix ──────────────────────────────────────
  form.addPageBreakItem().setTitle('G. Service mix');

  form.addCheckboxItem()
    .setTitle('Which services do you offer?')
    .setHelpText('Select all that apply.')
    .setChoiceValues([
      'Long-term residential nursing care',
      'Assisted living / independent senior living',
      'Day care',
      'Home care (carers visit residents at home)',
      'Respite care'
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Do you accept Singaporean residents?')
    .setChoiceValues(['Yes', 'No'])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Halal-certified kitchen?')
    .setChoiceValues([
      'Yes — JAKIM certified',
      'Yes — halal but not JAKIM-certified',
      'No',
      'Partially'
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Wheelchair accessible throughout?')
    .setChoiceValues(['Yes', 'Partially', 'No'])
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle('Languages spoken by staff')
    .setChoiceValues([
      'English',
      'Bahasa Melayu',
      'Mandarin',
      'Cantonese',
      'Hokkien',
      'Tamil'
    ])
    .showOtherOption(true)
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Do you have parking available for visitors?')
    .setChoiceValues(['Yes — ample parking', 'Yes — limited', 'Street parking only', 'No parking'])
    .setRequired(false);

  form.addMultipleChoiceItem()
    .setTitle('Do you accept residents under government subsidy or JKM welfare assistance?')
    .setChoiceValues(['Yes', 'No', 'On a case-by-case basis'])
    .setRequired(false);

  form.addMultipleChoiceItem()
    .setTitle('Religious or cultural character of the facility')
    .setHelpText('Families looking for a faith-aligned environment often ask this.')
    .setChoiceValues([
      'Non-denominational / open to all',
      'Islamic / Muslim-operated',
      'Christian-operated',
      'Buddhist-operated',
      'Hindu-operated',
      'Mixed / multi-faith'
    ])
    .showOtherOption(true)
    .setRequired(false);

  form.addTextItem()
    .setTitle('Facebook page URL (if any)')
    .setHelpText('e.g. https://www.facebook.com/yourfacility — helps families find your social presence.')
    .setRequired(false);

  // ─── Section H — Facility details (enrichment) ────────────────────
  form.addPageBreakItem()
    .setTitle('H. Facility details')
    .setHelpText('These questions help families understand what to expect before they visit. All optional — answer what you can.');

  form.addMultipleChoiceItem()
    .setTitle('Current availability')
    .setChoiceValues([
      'Beds available now',
      'Waitlist — under 1 month',
      'Waitlist — 1 to 3 months',
      'Waitlist — over 3 months',
      'Full — not accepting new residents'
    ])
    .setRequired(false);

  form.addMultipleChoiceItem()
    .setTitle('Minimum length of stay')
    .setChoiceValues([
      'No minimum',
      '1 month',
      '3 months',
      '6 months',
      '1 year or more'
    ])
    .showOtherOption(true)
    .setRequired(false);

  form.addCheckboxItem()
    .setTitle('Which resident profiles do you accept?')
    .setHelpText('Select all that apply.')
    .setChoiceValues([
      'Ambulant (can walk independently)',
      'Semi-ambulant (needs walking aid or supervision)',
      'Wheelchair-bound',
      'Bedridden',
      'Post-ICU / post-surgery step-down',
      'Early to moderate dementia',
      'Advanced dementia (including wandering behaviour)',
      'End-of-life / palliative stage'
    ])
    .setRequired(false);

  form.addTextItem()
    .setTitle('Visiting hours')
    .setHelpText('e.g. "Daily 10am – 8pm" or "Weekends only 2pm – 6pm"')
    .setRequired(false);

  form.addTextItem()
    .setTitle('Registered nurse (RN) to resident ratio — daytime')
    .setHelpText('e.g. "1 RN to 20 residents". Caregivers / nursing assistants are counted separately below.')
    .setRequired(false);

  form.addTextItem()
    .setTitle('Registered nurse (RN) to resident ratio — overnight')
    .setHelpText('e.g. "1 RN to 40 residents on-call". Enter "RN on-call only" if applicable.')
    .setRequired(false);

  form.addTextItem()
    .setTitle('Caregiver / nursing assistant to resident ratio — daytime')
    .setHelpText('e.g. "1 caregiver to 5 residents"')
    .setRequired(false);

  form.addTextItem()
    .setTitle('Caregiver / nursing assistant to resident ratio — overnight')
    .setHelpText('e.g. "1 caregiver to 10 residents"')
    .setRequired(false);

  form.addMultipleChoiceItem()
    .setTitle('Air-conditioning')
    .setChoiceValues([
      'Fully air-conditioned (all rooms and common areas)',
      'Partially air-conditioned (bedrooms only)',
      'Partially air-conditioned (common areas only)',
      'Fan-cooled throughout',
      'Mixed — varies by room type'
    ])
    .setRequired(false);

  form.addMultipleChoiceItem()
    .setTitle('What is the nearest hospital for emergencies?')
    .setHelpText('Name and approximate distance. Families want to know before an emergency happens.')
    .setChoiceValues([
      'Government hospital within 5 km',
      'Government hospital 5 – 15 km',
      'Private hospital within 5 km',
      'Private hospital 5 – 15 km'
    ])
    .showOtherOption(true)
    .setRequired(false);

  form.addMultipleChoiceItem()
    .setTitle('Deposit required on admission')
    .setChoiceValues([
      'No deposit',
      '1 month deposit',
      '2 months deposit',
      '3 months deposit'
    ])
    .showOtherOption(true)
    .setRequired(false);

  form.addMultipleChoiceItem()
    .setTitle('Year your facility was established')
    .setChoiceValues([
      'Before 2000',
      '2000 – 2009',
      '2010 – 2014',
      '2015 – 2019',
      '2020 or later'
    ])
    .setRequired(false);

  // ─── Section I — Consent ──────────────────────────────────────────
  form.addPageBreakItem().setTitle('I. Permission and consent');

  form.addCheckboxItem()
    .setTitle('Authorisation')
    .setChoiceValues([
      'I confirm I am authorised to provide this information on behalf of the ' +
      'facility, and I consent to NursingHomeGuide.my displaying this information ' +
      'on the facility\'s public profile, attributed as "self-reported by the ' +
      'operator" with today\'s date.'
    ])
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle('Acknowledgement')
    .setChoiceValues([
      'I understand that providing inaccurate information may result in the profile ' +
      'being flagged or marked as unverified.'
    ])
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('Anything else you\'d like us to know?')
    .setHelpText('Optional. Use this for clarifications, "limited" capability descriptions from section E, or anything we should know about your facility.');

  // ─── Link responses to master Sheet ───────────────────────────────
  let sheetMessage;
  try {
    form.setDestination(FormApp.DestinationType.SPREADSHEET, MASTER_SHEET_ID);
    sheetMessage = '✓ Form responses linked to a new tab in master Sheet';
  } catch (e) {
    sheetMessage = '⚠ Could not link to master Sheet (' + e.message + '). ' +
      'A standalone response Sheet will be created. Link to master manually if needed.';
  }

  // ─── Output ───────────────────────────────────────────────────────
  const log = [
    '',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'FORM CREATED — NursingHomeGuide.my Operator Intake',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    sheetMessage,
    '',
    'PUBLIC URL (send to operators):',
    '  ' + form.getPublishedUrl(),
    '',
    'EDIT URL (for tweaks later):',
    '  ' + form.getEditUrl(),
    '',
    'NEXT STEPS:',
    '  1. Open the public URL once to verify sections look right',
    '  2. In the Forms UI, click "⋮" (top right) → "Get pre-filled link"',
    '     to generate per-facility links with name + address pre-filled',
    '  3. Share via the WhatsApp / email templates in the SOP',
    '',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    ''
  ].join('\n');
  Logger.log(log);
}
