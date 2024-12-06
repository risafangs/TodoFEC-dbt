{% docs amndt_ind %}
    Amendment indicator. Indicates if the report being filed is new (N), an amendment (A) to a previous report, or a termination (T) report.
{% enddocs %}

{% docs cand_election_yr %}
    Candidate's election year from a Statement of Candidacy or state ballot list
{% enddocs %}

{% docs cand_id %}
    A 9-character alpha-numeric code assigned to a candidate by the Federal Election Commission. The candidate ID for a specific candidate remains the same across election cycles as long as the candidate is running for the same office.
{% enddocs %}

{% docs cand_ici %}
    C = Challenger  
    I = Incumbent  
    O = Open Seat is used to indicate an open seat; Open seats are defined as seats where the incumbent never sought re-election.
{% enddocs %}

{% docs cand_office_st %}
     House = state of race  
     President = US  
     Senate = state of race
{% enddocs %}

{% docs cand_pcc %}
    The ID assigned by the Federal Election Commission to the candidate's PCC (principal campaign committee) for a given election cycle.
 {% enddocs %}

{% docs cand_status %}
    C = Statutory candidate  
    F = Statutory candidate for future election  
    N = Not yet a statutory candidate    
    P = Statutory candidate in prior cycle  
{% enddocs %}

{% docs cmte_dsgn %}
    A = Authorized by a candidate  
    B = Lobbyist/Registrant PAC  
    D = Leadership PAC  
    J = Joint fundraiser  
    P = Principal campaign committee of a candidate  
    U = Unauthorized  
{% enddocs %}

{% docs cmte_filing_freq %}
    A = Administratively terminated  
    D = Debt  
    M = Monthly filer  
    Q = Quarterly filer  
    T = Terminated  
    W = Waived
{% enddocs %}

{% docs cmte_id %}
    A 9-character alpha-numeric code assigned to a committee by the Federal Election Commission. Committee IDs are unique and an ID for a specific committee always remains the same.
{% enddocs %}

{% docs cmte_tp %}
    Committee type. See codes: https://www.fec.gov/campaign-finance-data/committee-type-code-descriptions/
{% enddocs %}

{% docs cvg_end_dt %}
    Coverage end date. Through date.
{% enddocs %}

{% docs entity_tp %}
    ONLY VALID FOR ELECTRONIC FILINGS received after April 2002.  
    CAN = Candidate  
    CCM = Candidate committee  
    COM = Committee  
    IND = Individual (a person)  
    ORG = Organization (not a committee and not a person)  
    PAC = Political action committee  
    PTY = Party organization  
{% enddocs %}

{% docs file_num %}
    File number/report id. Unique report id.
{% enddocs %}

{% docs image_num %}
    11-digit Image Number Format  
    YYOORRRFFFF  
    YY - scanning year  
    OO - office (01 - House, 02 - Senate, 03 - FEC Paper, 90-99 - FEC Electronic)  
    RRR - reel number  
    FFFF- frame number    

    18-digit Image Number Format (June 29, 2015)  
    YYYYMMDDSSPPPPPPPP  
    YYYY - scanning year  
    MM - scanning month  
    DD - scanning day  
    SS - source (02 - Senate, 03 - FEC Paper, 90-99 - FEC Electronic)  
    PPPPPPPP - page (reset to zero every year on January 1)
{% enddocs %}

{% docs office_district %}
     Two-digit US House distirict of the office the candidate is running for. Presidential, Senate and House at-large candidates will have District 00.
{% enddocs %}

{% docs pty_affiliation %}
    The political party affiliation reported by the candidate. For more information about political party affiliation codes [see this list of political party codes](https://www.fec.gov/campaign-finance-data/party-code-descriptions/).
{% enddocs %}

{% docs rpt_tp %}
    Report type. See report type codes: https://www.fec.gov/campaign-finance-data/report-type-code-descriptions/
{% enddocs %}

{% docs sub_id %}
    FEC record number and unique row ID
{% enddocs %}

{% docs tran_id %}
    ONLY VALID FOR ELECTRONIC FILINGS. A unique identifier associated with each itemization or transaction appearing in an FEC electronic file. A transaction ID is unique for a specific committee for a specific report. In other words, if committee, C1, files a Q3 New with transaction SA123 and then files 3 amendments to the Q3 transaction SA123 will be identified by transaction ID SA123 in all 4 filings.
{% enddocs %}

{% docs transaction_pgi %}
    Primary general indicator.
{% enddocs %}

{% docs tres_nm %}
    The officially registered treasurer for the committee.
{% enddocs %}

