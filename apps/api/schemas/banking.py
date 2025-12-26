from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict

# Banking & Finance Schema

class CustomerIdentity(BaseModel):
    model_config = ConfigDict(extra='forbid')
    fullLegalName: Optional[str] = Field(None, description="Full Legal Name")
    borrowerName: Optional[str] = Field(None, description="Borrower Name")
    governmentIdType: Optional[str] = Field(None, description="Government-Issued ID Type and Number")
    socialInsuranceNumber: Optional[str] = Field(None, description="Social Insurance Number (SIN) / SSN")
    dateOfBirth: Optional[str] = Field(None, description="Date of Birth (MM/DD/YYYY)")
    nationality: Optional[str] = Field(None, description="Nationality / Citizenship")
    emailAddress: Optional[str] = Field(None, description="Email Address")
    phoneNumber: Optional[str] = Field(None, description="Phone Number")
    currentPreviousAddress: Optional[str] = Field(None, description="Address (Current and Previous)")
    maritalStatus: Optional[str] = Field(None, description="Marital Status")
    numberOfDependents: Optional[str] = Field(None, description="Number of Dependents")
    employerName: Optional[str] = Field(None, description="Employer Name")
    employmentStatus: Optional[str] = Field(None, description="Employment Status")
    employedSince: Optional[str] = Field(None, description="Employed Since")
    occupation: Optional[str] = Field(None, description="Occupation")
    annualIncome: Optional[str] = Field(None, description="Annual Income (with $ prefix)")
    sourceOfFunds: Optional[str] = Field(None, description="Source of Funds")
    pepDeclaration: Optional[str] = Field(None, description="PEP Declaration (Politically Exposed Person)")

class Customer(BaseModel):
    model_config = ConfigDict(extra='forbid')
    identity: CustomerIdentity

class Mortgage(BaseModel):
    model_config = ConfigDict(extra='forbid')
    loanId: Optional[str] = Field(None, description="Loan ID / Mortgage Number")
    mortgageId: Optional[str] = Field(None, description="Mortgage ID/Loan Number")
    typeOfLoan: Optional[str] = Field(None, description="Type of Loan")
    typeOfMortgage: Optional[str] = Field(None, description="Type of Mortgage (Fixed/ARM/FHA/etc.)")
    loanAmount: Optional[str] = Field(None, description="Loan Amount (with $ prefix)")
    approvedLoanAmount: Optional[str] = Field(None, description="Approved Loan Amount (with $ prefix)")
    loanTerm: Optional[str] = Field(None, description="Loan Term (Years)")
    monthlyPaymentAmount: Optional[str] = Field(None, description="Monthly Payment Amount (with $ prefix)")
    paymentFrequency: Optional[str] = Field(None, description="Payment Frequency")
    paymentDueDates: Optional[str] = Field(None, description="Payment Due Dates")
    interestRate: Optional[str] = Field(None, description="Interest Rate (Fixed/Variable)")
    prepaymentPenalty: Optional[str] = Field(None, description="Prepayment Penalty")
    loanApprovalDate: Optional[str] = Field(None, description="Loan Approval Date")
    loanClosingDate: Optional[str] = Field(None, description="Loan Closing Date")
    outstandingLoanBalance: Optional[str] = Field(None, description="Outstanding Loan Balance (with $ prefix)")
    loanStatus: Optional[str] = Field(None, description="Loan Status (Active/Delinquent/Closed)")
    latePaymentHistory: Optional[str] = Field(None, description="Late Payment History")
    creditReport: Optional[str] = Field(None, description="Credit Report (Credit Score)")
    foreclosureDefaultStatus: Optional[str] = Field(None, description="Foreclosure/Default Status (If Applicable)")
    digitalSignatureDate: Optional[str] = Field(None, description="Digital Signature Date")

class Loan(BaseModel):
    model_config = ConfigDict(extra='forbid')
    mortgage: Mortgage

class Property(BaseModel):
    model_config = ConfigDict(extra='forbid')
    propertyAddress: Optional[str] = Field(None, description="Property Address")
    propertyType: Optional[str] = Field(None, description="Property Type (Residential/Commercial)")
    appraisedValue: Optional[str] = Field(None, description="Appraised Value (with $ prefix)")
    downPayment: Optional[str] = Field(None, description="Down Payment (with $ prefix)")
    escrowAccountDetails: Optional[str] = Field(None, description="Escrow Account Details")
    mortgageInsuranceRequired: Optional[str] = Field(None, description="Mortgage Insurance Required (Yes/No)")
    lienPosition: Optional[str] = Field(None, description="Lien Position")
    reverseMortgageTerms: Optional[str] = Field(None, description="Reverse Mortgage Terms")
    sharedEquityMortgageInfo: Optional[str] = Field(None, description="Shared Equity Mortgage Information")
    sharedAppreciationMortgageInfo: Optional[str] = Field(None, description="Shared Appreciation Mortgage Information")
    fixedRateMortgageDetails: Optional[str] = Field(None, description="Fixed-Rate Mortgage Details")
    adjustableRateMortgageInfo: Optional[str] = Field(None, description="Adjustable-Rate Mortgage Information")
    interestOnlyMortgageTerms: Optional[str] = Field(None, description="Interest-Only Mortgage Terms")
    conventionalMortgageTerms: Optional[str] = Field(None, description="Conventional Mortgage Terms")
    greenMortgageDetails: Optional[str] = Field(None, description="Green Mortgage Details")
    homeEquityLoanDetails: Optional[str] = Field(None, description="Home Equity Loan Details")
    helocDetails: Optional[str] = Field(None, description="Home Equity Line of Credit (HELOC)")
    bridgeLoanDetails: Optional[str] = Field(None, description="Bridge Loan Details")
    constructionLoanDetails: Optional[str] = Field(None, description="Construction Loan Details")
    insuredMortgage: Optional[str] = Field(None, description="Insured Mortgage (CMHC-backed/etc.)")
    titleDeedNumber: Optional[str] = Field(None, description="Title Deed Number")

class Credit(BaseModel):
    model_config = ConfigDict(extra='forbid')
    personalLoanDetails: Optional[str] = Field(None, description="Personal Loan Details")
    autoLoanTerms: Optional[str] = Field(None, description="Auto Loan Terms")
    studentLoanInfo: Optional[str] = Field(None, description="Student Loan Information")
    creditCardLoanInfo: Optional[str] = Field(None, description="Credit Card Loan Information")
    debtConsolidationDetails: Optional[str] = Field(None, description="Debt Consolidation Loan Details")
    linesOfCreditDetails: Optional[str] = Field(None, description="Lines of Credit Details")
    lineOfCreditUtilizationRate: Optional[str] = Field(None, description="Line of Credit Utilization Rate")
    creditLimit: Optional[str] = Field(None, description="Credit Limit")
    creditScore: Optional[str] = Field(None, description="Credit Score (Internal or Bureau)")
    coSignerGuarantorInfo: Optional[str] = Field(None, description="Co-Signer or Guarantor Information")
    paydayLoanInfo: Optional[str] = Field(None, description="Payday Loan Information")
    minimumPaymentDue: Optional[str] = Field(None, description="Minimum Payment Due")

class Business(BaseModel):
    model_config = ConfigDict(extra='forbid')
    smallBusinessLoanInfo: Optional[str] = Field(None, description="Small Business Loan Information")
    businessLineOfCreditDetails: Optional[str] = Field(None, description="Business Line of Credit Details")
    commercialRealEstateLoanDetails: Optional[str] = Field(None, description="Commercial Real Estate Loan Details")
    equipmentFinancingTerms: Optional[str] = Field(None, description="Equipment Financing Loan Terms")
    invoiceFactoringDetails: Optional[str] = Field(None, description="Invoice Factoring Details")
    workingCapitalLoanInfo: Optional[str] = Field(None, description="Working Capital Loan Information")
    merchantCashAdvanceTerms: Optional[str] = Field(None, description="Merchant Cash Advance Terms")

class Government(BaseModel):
    model_config = ConfigDict(extra='forbid')
    fhaVaLoanDetails: Optional[str] = Field(None, description="FHA and VA Loan Details (U.S.)")
    sbaLoanInfo: Optional[str] = Field(None, description="SBA Loan Information (U.S.)")
    cmhcLoanDetails: Optional[str] = Field(None, description="CMHC Loan Details (Canada)")
    firstTimeBuyerIncentive: Optional[str] = Field(None, description="First-Time Home Buyer Incentive (Canada)")

class BankingDetails(BaseModel):
    model_config = ConfigDict(extra='forbid')
    accountNumber: Optional[str] = Field(None, description="Account Number / IBAN")
    accountType: Optional[str] = Field(None, description="Account Type (Savings/Checking)")
    currency: Optional[str] = Field(None, description="Currency")
    transactionId: Optional[str] = Field(None, description="Transaction ID")
    dateTime: Optional[str] = Field(None, description="Date and Time")
    amount: Optional[str] = Field(None, description="Amount (Debit/Credit) (with $ prefix)")
    merchantName: Optional[str] = Field(None, description="Merchant Name / Payee")
    description: Optional[str] = Field(None, description="Description / Memo")
    availableBalance: Optional[str] = Field(None, description="Available Balance (with $ prefix)")
    postedBalance: Optional[str] = Field(None, description="Posted Balance (with $ prefix)")
    channel: Optional[str] = Field(None, description="Channel (ATM/POS/Online)")
    authorizationCode: Optional[str] = Field(None, description="Authorization Code")

class Financial(BaseModel):
    model_config = ConfigDict(extra='forbid')
    claimProductAmountRequested: Optional[str] = Field(None, description="Claim/Product Amount Requested (with $ prefix)")
    settlementAmountOffered: Optional[str] = Field(None, description="Settlement Amount Offered (with $ prefix)")
    legalAdministrativeCosts: Optional[str] = Field(None, description="Legal and Administrative Costs (with $ prefix)")
    debtToIncomeRatio: Optional[str] = Field(None, description="Debt-to-Income (DTI) Ratio")
    liquidityRatio: Optional[str] = Field(None, description="Liquidity Ratio")
    collateralCoverageRatio: Optional[str] = Field(None, description="Collateral Coverage Ratio")
    netWorthEstimate: Optional[str] = Field(None, description="Net Worth Estimate (with $ prefix)")
    riskScore: Optional[str] = Field(None, description="Risk Score / Internal Rating")
    incomeVerificationType: Optional[str] = Field(None, description="Income Verification Type")
    regulatoryCertificateRef: Optional[str] = Field(None, description="Regulatory Certificate Reference #")

class Compliance(BaseModel):
    model_config = ConfigDict(extra='forbid')
    amlKycVerificationResult: Optional[str] = Field(None, description="AML/KYC Verification Result")
    fatcaStatus: Optional[str] = Field(None, description="FATCA Status")
    consentForCreditCheck: Optional[str] = Field(None, description="Consent for Credit Check")
    gdprPrivacyConsent: Optional[str] = Field(None, description="GDPR/Privacy Consent")
    intendedUseOfAccount: Optional[str] = Field(None, description="Intended Use of Account")
    sanctionsBlacklistScreening: Optional[str] = Field(None, description="Sanctions/Blacklist Screening")
    documentChecklistCompletion: Optional[str] = Field(None, description="Document Checklist Completion")

class Operational(BaseModel):
    model_config = ConfigDict(extra='forbid')
    dateOfApplication: Optional[str] = Field(None, description="Date of Application")
    branchCode: Optional[str] = Field(None, description="Branch Code")
    applicationStatus: Optional[str] = Field(None, description="Application Status (In Review/Approved/Rejected)")
    officerAgentName: Optional[str] = Field(None, description="Officer/Agent Name")
    underwriterNotes: Optional[str] = Field(None, description="Underwriter Notes")
    eSignatureConfirmation: Optional[str] = Field(None, description="E-Signature Confirmation")
    submissionChannel: Optional[str] = Field(None, description="Submission Channel (Online/Branch)")

class Summary(BaseModel):
    model_config = ConfigDict(extra='forbid')
    keyFindingsAnalysis: Optional[str] = Field(None, description="Key Findings and Analysis")
    recommendationsRiskMitigation: Optional[str] = Field(None, description="Recommendations for Risk Mitigation")
    futurePolicyProductAdjustments: Optional[str] = Field(None, description="Future Policy or Product Adjustments")

class BankingExtraction(BaseModel):
    model_config = ConfigDict(extra='forbid')
    customer: Optional[Customer]
    loan: Optional[Loan]
    property: Optional[Property]
    credit: Optional[Credit]
    business: Optional[Business]
    government: Optional[Government]
    banking: Optional[BankingDetails]
    financial: Optional[Financial]
    compliance: Optional[Compliance]
    operational: Optional[Operational]
    summary: Optional[Summary]
    confidence_report: Optional[Dict[str, float]] = Field(
        None, 
        description="Dictionary mapping field paths (e.g. 'customer.identity.borrowerName') to their confidence score (0.0-1.0). You MUST include a score for EVERY extracted non-null field in the entire object."
    )
