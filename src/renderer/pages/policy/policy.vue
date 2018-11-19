<template lang="pug">
  .page_policy
    router-link(:to="{name: 'register'}").btn.btn--link Back to registarion  
    .heading
      h2 Terms of Use
      p Updated December 20, 2017
    .intro
      p
        | THE TERMS OF THIS MASTER SERVICES AGREEMENT (
        strong
          | “
          em AGREEMENT
        | ”) GOVERN YOUR USE OF THE APPLICATION SERVICES (AS DEFINED BELOW) OF MIXPANEL, INC. (“
        strong
          em MIXPANEL
        | ”). IF YOU DO NOT AGREE TO THESE TERMS, DO NOT USE MIXPANEL’S APPLICATION SERVICES. BY ACCEPTING THESE TERMS BELOW OR BY USING MIXPANEL’S APPLICATION SERVICES IN ANY MANNER, YOU, THE ENTITY YOU REPRESENT AND ANY AFFILIATE OF SUCH ENTITY (COLLECTIVELY, “
        strong
          em CUSTOMER
        | ”) AGREE THAT YOU HAVE READ AND AGREE TO BE BOUND BY THIS AGREEMENT TO THE EXCLUSION OF ALL OTHER TERMS. IF THE TERMS OF THIS AGREEMENT ARE CONSIDERED AN OFFER, ACCEPTANCE IS EXPRESSLY LIMITED TO SUCH TERMS. THIS AGREEMENT IS ENTERED INTO AS OF THE DATE YOU ACCEPT THESE TERMS OR USE THE APPLICATION SERVICES (“
        strong
          em EFFECTIVE DATE
        | ”).
    .ordered-article
      h3 1. LICENSE TO USE THE SERVICES
      p
        | 1.1 Subject to the terms of this Agreement, Mixpanel grants to Customer a limited, non-exclusive, non-transferable right to access and use the Application Services, and allow its Authorized Users to access and use the Application Services, solely for Customer’s internal business purposes and not for resale or further distribution. Customer’s right to use the Application Services is limited by all terms and conditions herein. Customer shall be responsible for its Authorized Users in compliance with Customer’s obligations under the terms of the Agreement. Except for this license granted to Customer, Mixpanel and its licensors retain all right, title and interest in and to the Application Services, including all related intellectual property rights. The Application Services are protected by applicable intellectual property laws, including U.S. copyright law and international treaties. “
        em
          strong Authorized User
        | ” means any individual provided with access to the Application Services by Customer.  “
        em
          strong Application Services
        | ” shall mean the online, web-based and mobile-based applications ordered by Customer through either: (i) Customer’s selection and acceptance of a specific pricing plan and volume tier for the Application Services, which are set forth at 
        
        |  (the “
        em
          strong Pricing Page
        | ”) via the online purchasing process at 
        
        | , or (ii) an Order Form, in each case provided by Mixpanel via 
        
        |  or other designated websites or IP addresses or mobile applications, as communicated to Customer by Mixpanel. An “
        em
          strong Order Form
        | ” shall mean means an ordering document, including without limitation statements of work, signed by both parties and incorporating the terms of this Agreement by reference, that specifies the Application Services purchased by Customer.  An “
        em
          strong Affiliate
        | ” means an entity which, directly or indirectly, owns or controls, is owned or is controlled by or is under common ownership or control with a party. As used herein, “
        em
          strong control
        | ” means the power to direct the management or affairs of an entity, and “
        em
          strong ownership
        | ” means the beneficial ownership of fifty percent (50%) or more of the voting equity securities or other equivalent voting interests of the entity.
      p
        | 1.2 
        strong Pricing Plans.  
        | Mixpanel’s Application Services are comprised of People Plans for the purchase of “people profiles” and Engagement Plans for the purchase of “data points,” which can be purchased separately or jointly, each with features and functionality set forth on the Pricing Page.  For Application Services provided on a People Plan basis, a “
        em
          strong people profile
        | ” is a JSON object comprised of an identifier or identifying string intended to indicate a unique user and a dictionary of properties (object) that is stored by the Application Services.  For Application Services provided on an Engagement Plan basis, a “
        em
          strong data point
        | ” is a JSON object comprised of an event (string) and a dictionary of properties (object) that is stored by the Application Services.  Mixpanel supports certain legacy pricing plans which remain grandfathered in until the end of their current term or as otherwise terminated.  Mixpanel reserves the right to discontinue supporting legacy pricing plans at any time with prior notice.  Mixpanel may modify its Pricing Page at any time and add new services or pricing plans for additional fees and charges, or amend fees and charges for existing services, at any time and in its sole discretion without prior notice to you.
      p
        | 1.3 
        strong Free Services. 
        |  Mixpanel’s Free People Plan and Free Engagement Plan are each offered at no charge, but have limited people profiles and data points, respectively, as well as limited features and functionality, as set forth on the Pricing Page.  Both plans have a monthly term and automatically renew unless Customer terminates the applicable plan by writing to Mixpanel at 
        
        | , Mixpanel terminates the Agreement or Customer otherwise purchases a paid plan.  Mixpanel may modify the services offered with either free plan at any time in its sole discretion or even discontinue them entirely without prior notice to you.
      p
        | 1.4 
        strong Paid Services.
      p
        | (i) 
        strong People Plans. 
        strong  
        | Mixpanel offers People Plans with a length of term and in the volume tiers set forth on the Pricing Page.  In addition, Mixpanel offers an Enterprise People Plan with custom people profile volumes that may only be purchased by Customer through execution of an Order Form.  These People Plans are all billed in advance of their respective terms and automatically renew at the end of their respective terms for an equivalent term, or as otherwise stated in the Order Form, unless Customer chooses not to renew such plan by writing to Mixpanel at 
        |  or Mixpanel terminates the Agreement.  The number of people profiles purchased by Customer in a given volume tier of People Plan is the maximum number of people profiles that Customer may have at the end of each month of a given term.  In the event Customer’s count of people profiles at the end of any month during a given term exceeds the volume tier selected by Customer, Mixpanel will charge additional fees (“
        em
          strong People Overage Fees
        | ”) at 120% of the unit price applicable to Customer’s selected volume tier and the Customer shall be obligated to pay any People Overage Fees in the next month.  Customer may upgrade and purchase a higher volume tier of a People Plan at any time through the Application Services by paying the price of the higher volume tier.  Upon such upgrade, Customer will be allocated the number of people profiles for such higher volume tier through the remainder of the applicable term.
      p
        | (ii) 
        strong Engagement Plans.  
        | Mixpanel offers Engagement Plans with a length of term and in the volume tiers set forth on the Pricing Page.  In addition, Mixpanel offers an Enterprise Engagement Plan with custom data point volumes, features, support and services that may only be purchased by Customer through execution of an Order Form.  These Engagement Plans are all billed in advance of their respective terms and automatically renew at the end of their respective terms for an equivalent term, or as otherwise stated in the Order Form, unless Customer chooses not to renew such plan by writing to Mixpanel at 
        
        |  or Mixpanel terminates the Agreement.  The number of data points purchased by Customer in a given volume tier of an Engagement Plan must be used during each applicable term and any unused data points at the end of such term are forfeited.  In the event Customer’s usage of data points exceeds the volume tier selected by Customer during a given term, Mixpanel will thereafter through the end of such term charge additional fees (“
        em
          strong Event Overage Fees
        | ”) at 120% of the unit price applicable to Customer’s selected volume tier and the Customer shall be obligated to pay any Event Overage Fees in the next month.  Customer may upgrade and purchase a higher volume tier at any time through the Application Services by paying the price of the higher volume tier.  Upon such upgrade, Customer will receive additional data points equal to the net difference between the purchased higher volume tier and Customer’s current volume tier (such incremental amount, the “
        em
          strong Upgrade Bundle
        | ”).  The Upgrade Bundle must be used during the remainder of the applicable term in which it was purchased, otherwise it will be forfeited.
      p
        | To the extent of any conflict or inconsistency between the foregoing provisions in Section 1 of this Agreement and any Order Form, the terms of such Order Form shall prevail and govern Customer’s use and purchase of the Application Services.  For purposes herein, “
        em
          strong Overage Fees
        | ” shall mean People Overage Fees and Event Overage Fees collectively.
      p
        | 1.5 Fees paid hereunder, including Overage Fees, are non-refundable and shall be billed in U.S. Dollars. Except as otherwise set forth in an Order Form, fees due hereunder will be billed to Customer’s credit card and Customer authorizes the card issuer to pay all such amounts and authorizes Mixpanel (or its billing agent) to charge the credit card account until Customer or Mixpanel cancels or terminates the Application Services as set forth herein; provided that if payment is not received from the credit card issuer, Customer agrees to pay all amounts due upon demand. Customer must provide current, complete and accurate billing and credit card information. Customer agrees to pay all costs of collection, including attorney’s fees and costs, on any outstanding balance. In certain instances, the issuer of the credit card may charge a foreign transaction fee or related charges, which Customer shall be responsible to pay.
      p
        | 1.6 Fees do not include any local, state, federal or foreign taxes, levies, duties or similar governmental assessments of any nature, including value-added, use or withholding taxes (collectively, “
        em
          strong Taxes
        | ”). Customer is responsible for payment of all Taxes associated with its purchases hereunder (excluding taxes based on Mixpanel’s net income or property), and any related penalties and interest. Customer will make all required payments to Mixpanel free and clear of, and without reduction for, any withholding taxes. Customer will, upon Mixpanel’s request, provide Mixpanel with official receipts issued by appropriate taxing authorities, or such other evidence as Mixpanel may reasonably request, to establish that such Taxes have been paid.
      h3 2. ACCESS TO THE SERVICES
      p
        | 2.1 Mixpanel does not provide the equipment required to access the Application Services. Customer is responsible for all fees charged by third parties related to Customer’s access and use of the Application Services (e.g., charges by Internet service providers).  In the event Customer utilizes SMS notifications as part of its utilization of the Application Services, Mixpanel reserves the right to pass through its costs of such service to Customer, and Customer agrees to be pay such fees.
      p
        | 2.2 Mixpanel also reserves the right to restrict, suspend, or terminate access to the Application Services at any time, if in Mixpanel’s sole determination, Customer is using the Application Services in a manner that violates applicable laws or the terms of this Agreement, fails to make payment to Mixpanel or creates an Excess Burden on Mixpanel’s systems.  “
        em
          strong Excess Burden
        | ” means when the Application Services are being used to engage in denial of service attacks, spamming, or any illegal activity, and/or use of Application Services is causing immediate, material and ongoing harm to Mixpanel or Mixpanel’s other customers.
      p
        | 2.3 Mixpanel does not provide maintenance for or guarantee the continued function of, and Mixpanel reserves the right to change, discontinue, delete and/or deprecate, at any time and at Mixpanel’s sole discretion, any product feature, support service and any custom report template that may be made available to or accessible by Customer, including through the Application Services.  Custom reports could include, but are not limited to, custom JQL queries, ReportKit Applications, or other reports customized for Customer’s use.
      p
        | 2.4 From time to time, Mixpanel may make Beta Services (as defined below) available to Customer at no charge.  Customer may choose to utilize such Beta Services in Customer’s sole discretion.  Beta Services are intended for evaluation purposes and not for production use, are not fully supported and may be subject to additional terms that may be presented to Customer.  Beta Services are provided on an “as-is” and “as available” basis without any warranty, support, maintenance, storage, service-level agreement or indemnity obligation of any kind and so, are not considered “Application Services” hereunder, even if displayed in the user interface; however, all restrictions herein, Mixpanel’s reservation of rights and Customer’s obligations concerning the Application Services shall apply equally to Mixpanel’s use of Beta Services.  Mixpanel may discontinue Beta Services at any time in its sole discretion and may never make them generally available.  Mixpanel will have no liability for any harm or damage arising out of or in connection with a Beta Service.  “
        em
          strong Beta Services
        | ” means a product, service or functionality provided by Mixpanel that may be made available to Customer to try at Customer’s option at no additional charge which is clearly designated as beta, pilot, limited release, non-production, early access, evaluation or by a similar description.  Beta Services may be considered Confidential Information of Mixpanel, if so denoted or communicated by Mixpanel to Customer.  Customer will not disclose (including, but not limited to, in a press release or public statement) any information about, involving or regarding Beta Services (including the existence of), except as agreed by Mixpanel in writing.
      h3 3. RESTRICTIONS
      p
        | Customer shall use the Application Services only in compliance with all applicable laws, including any applicable privacy laws, and the terms of this Agreement. Customer shall not and shall not permit or authorize any third party to: (i) copy, rent, sell, lease, sublicense, distribute, assign, or otherwise transfer or encumber rights to the Application Services, or use the Application Services for the benefit of any third party, or make the Application Services available to anyone other than its Authorized Users; (ii) use the Application Services to send spam or otherwise duplicative or unsolicited messages in violation of applicable laws, or to process, send or store Sensitive Information, infringing or unlawful material, viruses, worms, time bombs, Trojan horses or other harmful or malicious code, files, scripts, agents or programs; (iii) circumvent or disable any digital rights management, usage rules, or other security features of the Application Services, or otherwise attempt to gain unauthorized access to, or disrupt the integrity or performance of, the Application Services or the data contained therein; (iv) modify, copy, translate, enhance, decompile, disassemble, reverse engineer or create derivative works based on the Application Services, or any portion thereof; (v) access or use the Application Services for the purpose of building a competitive product or service or copying its features or user interface; (vi) remove, alter, or obscure any copyright, trademark or other proprietary notices appearing in or on the Application Services; or (vi) use the Application Services in a manner that overburdens, or that threatens the integrity, performance, or availability of, the Application Services.
      h3 4. PRIVACY POLICY
      p
        | 4.1 To the extent Customer Content that includes Personal Information is sent by Customer through the Application Services and Customer’s use of the Application Services involves transferring Personal Information outside the European Economic Area or Switzerland to any country not deemed by the European Commission as providing an adequate level of protection for  personal data, the terms of the Data Processing Addendum available at 
        
        |  shall apply to such Personal Information and be incorporated into the Agreement. Customer Content shall be hosted and persistently stored by Mixpanel or its third-party service providers in the United States. In providing the Application Services, Mixpanel may engage sub-processors to process Customer Content, including, without limitation, any associated Personal Information pursuant to this Agreement within the European Economic Area, the United States and in other countries and territories. Under no circumstances will Mixpanel be deemed a data controller with respect to Customer Content under the Data Protection Act (European Directive 95/46/EC) or any relevant or replacement law or regulation of any Member State as defined therein. “
        strong
          em Personal Information
        | ” means any Customer Content processed by Mixpanel pursuant to the Agreement, relating to an identified or identifiable natural person; where an “identifiable natural person” means an individual who can be identified, directly or indirectly, in particular by reference to an identification number or to one or more factors specific to the individual’s physical, physiological, mental, economic, cultural or social identity.
      p
        | 4.2 The Application Services are designed to allow Customer to learn how a user of Customer’s mobile applications, mobile websites, web connected devices or web properties with which Customer has integrated the Application Services  (“
        em
          strong End Users
        | ”) use Customer’s mobile applications, mobile websites, web connected devices or web properties by giving Customer the ability to collect data, media and other information provided by or on behalf of Customer to the Application Services, excluding Sensitive Information (collectively, “
        em
          strong Customer Content
        | ”). Mixpanel does this in part using a first party cookie placed on End User’s device from Customer’s server. Some information is automatically collected from or about End Users when Customer uses the Application Services. If Customer integrates an official Mixpanel iOS, Android, BlackBerry, ActionScript, Java, Ruby, Python, PHP C++ or JavaScript library in Customer’s mobile applications, mobile websites or web properties it may by default collect Customer Content including but not limited to: the time of an event, the elements an End User has interacted with, metadata and other details about these elements including duration of interaction, how an End User came to Customer’s site, what search engine and search keywords End Users may have used to get to Customer’s site, information about the device an End User is on such as their operating system and browser, as well as the city/country location of End Users, tokens and IDs for push notifications. In addition, Customer can choose what other Customer Content Customer wants to collect such as age, IP addresses, user names, real names, email addresses and other custom properties. If Customer uses the Mixpanel Messages service, the emails Customer send to End Users through the Application Services may contain web beacons. Mixpanel uses web beacons on Customer’s behalf to track when a user opens and acts upon Customer’s emails.
      p
        | 4.3 Customer agrees to comply with all applicable privacy and data protection regulations. Further, Customer agrees to not use the Application Services to send Mixpanel Sensitive Information. “
        em
          strong Sensitive Information
        | ” shall means information the unauthorized disclosure of which could cause material, severe, or catastrophic harm or impact to Mixpanel, any data subjects or third parties, including but not limited to passwords, authentication/authorization credentials, business secrets deemed highly confidential (e.g., highly-confidential business strategies and communications, sensitive attorney-client privileged and confidential communications), and information under regulatory or contractual handling requirements (e.g., Payment Card Industry Data Security Standards) including without limitation: credit card information, credit card numbers and magnetic stripe information, social security numbers, driver’s license numbers, passport numbers, government issued identification numbers, financial account information, genetic, bio-metric, or health data, personally identifiable information collected from children under the age of 13 or from online services directed toward children, and real time geo-location data which can identify an individual.
      p
        | 4.4 Mixpanel collects, stores, uses and accesses Customer Content to maintain, improve and support the Application Services. Mixpanel may also use Customer Content in an encrypted and aggregated form (“
        em
          strong Aggregated Data
        | ”) for Mixpanel’s own business purposes, including use, duplication, modification and creation of derivative works regarding usage and performance of Aggregated Data which does not directly or indirectly identify Customer or End Users.  Mixpanel shall own all right, title and interest to the Aggregated Data and any derivative works thereof. Mixpanel only shares Customer Content with others under special circumstances as follows:
      p
        | a. With third parties who work on Mixpanel’s behalf to provide the Application Services;
      p
        | b. To the extent needed to comply with laws or to respond to lawful requests and legal process (provided that Mixpanel will endeavor to notify Customer if Mixpanel has received a lawful request for Customer’s information);
      p
        | c. To protect the rights and property of Mixpanel, its agents, customers, and others including to enforce Mixpanel’s agreements, policies, and terms of use;
      p d. In an emergency, including to protect the personal safety of any person;
      p
        | e. In connection with a sale or transfer of all or a part of Mixpanel’s business or assets (business deals may include, for example, any merger, financing, acquisition, divestiture, or bankruptcy transaction or proceeding); or
      p
        | f. As directed by Customer, including through its use of the Application Services.
      p
        | 4.5 Mixpanel provides Customer with access to Customer Content and the ability to delete Customer Content upon request.  Upon cessation of Mixpanel’s relationship with Customer, Mixpanel may delete Customer Content no longer in active use.  Mixpanel agrees to maintain commercially reasonable technical and organizational measures designed to safeguard Customer Content from unauthorized access, use or disclosure. These will include measures designed to: (i) store Customer Content on servers located in a physically secured location and (ii) use firewalls, access controls and similar security technology designed to protect Customer Content from unauthorized disclosure.  Mixpanel takes no responsibility and assumes no liability for any Customer Content other than its express security obligations in this section.
      p
        | 4.6 End Users can opt-out of Mixpanel’s automatic retention of data collected through their web browsers while on Customer’s mobile and web properties or websites that have the Application Services integrated by visiting 
        
        | . To track opt-outs, Mixpanel uses a persistent opt-out cookie placed on devices of End Users. Mixpanel opt-out cookies will not stop Customer from sending other data about that End User from Customer’s servers to Mixpanel, nor will it prevent any other data collection methods.
      p
        | 4.7 Customer agrees to provide appropriate notices to its End Users about, and if required by applicable laws obtain appropriate consent from such End Users for, Customer’s information collection and use practices relating to Customer’s use of the Application Services and Customer’s use of cookies for tracking purposes. Appropriate notices may include notice in the form of a privacy policy posted on Customer’s site, in Customer’s mobile application, and/or, if Customer uses Mixpanel Messages (as discussed in further detail below), in the emails Customer sends through the Application Services. Customer also agrees to include a notice about the Mixpanel opt-out for Customer’s site and the Mixpanel opt-out link in Customer’s privacy policy or in a notice on Customer’s website(s). Customer will also inform its End Users that if they get a new computer, install a new browser, erase or otherwise alter their browser’s cookie file (including upgrading certain browsers) they may also clear the Mixpanel opt-out cookie.
      p
        | 4.8 Mixpanel may also collect registration and other information about Customer through Mixpanel’s website. Mixpanel’s collection and use of information collected about Customer on Mixpanel’s website is governed by the Mixpanel Privacy Statement, available at 
        | . The Mixpanel Privacy Statement does not cover information Mixpanel collects on Customer’s behalf from Customer’s mobile and web properties. It is Customer’s obligation to provide Customer’s own privacy policy or notice to Customer’s users.
      h3 5. RESTRICTED AREAS OF THE SERVICES
      p
        | Certain parts of the Application Services, including account management features, may be password-restricted to registered users or other authorized persons (“
        em
          strong Password-Protected Areas
        | ”). If Customer is authorized to gain access to any Password-Protected Areas, Customer agrees that Customer is entirely responsible for maintaining the confidentiality of Customer’s password, and agrees to notify Mixpanel if the password is lost, stolen, disclosed to an unauthorized third party, or otherwise may have been compromised. Customer agrees that Customer is entirely responsible for any and all activities that occur under Customer’s account, whether or not Customer undertakes such activities. Customer agrees to immediately notify Mixpanel of any unauthorized use of Customer’s account or any other breach of security in relation to Customer’s password or the Application Services that is known to Customer.
      h3 6. LINKS AND THIRD PARTY CONTENT
      p
        | 6.1 The Application Services may display, or contain links to, third party products, services, and websites. Any opinions, advice, statements, services, offers, or other information that constitutes part of the content expressed, authored, or made available by other users or other third parties on the Application Services, or which is accessible through or may be located using the Application Services (collectively, “
        em
          strong Third Party Content
        | ”) are those of the respective authors or producers and not of Mixpanel or its stockholders, directors, officers, employees, agents, or representatives.
      p
        | 6.2 Mixpanel does not control Third Party Content and does not guarantee the accuracy, integrity or quality of such Third Party Content. Mixpanel is not responsible for the performance of, does not endorse, and is not responsible or liable for, any Third Party Content or any information or materials advertised in any Third Party Content. By using the Application Services, Customer may be exposed to content that is offensive, indecent, or objectionable. Mixpanel is not be responsible or liable, directly or indirectly, for any damage or loss caused to Customer by Customer’s use of or reliance on any goods, services, or information available on or through any third party service or Third Party Content. It is Customer’s responsibility to evaluate the information, opinion, advice, or other content available on and through the Application Services.
      p
        | 6.3 Customer will not use the Application Services to: (i) upload, post, email, or otherwise transmit any content that contains unlawful, harmful, threatening, abusive, harassing, tortious, defamatory, vulgar, obscene, libelous, invasive of another’s privacy, hateful, or racially, ethnically or otherwise objectionable; (ii) harm Mixpanel or third parties in any way; (iii) impersonate any person or entity, or otherwise misrepresent Customer’s affiliation with a person or entity; (iv) upload, post, email, or otherwise transmit any content that Customer does not have a right to transmit under any law or under contractual or fiduciary relationships (such as inside information, proprietary and confidential information learned or disclosed as part of employment relationships or under nondisclosure agreements); (v) upload, post, email or otherwise transmit any content that infringes any patent, trademark, trade secret, copyright, or other right of any party; (vi) upload, post, email, or otherwise transmit any unsolicited or unauthorized advertising, promotional materials, “junk mail,” “spam,” “chain letters,” “pyramid schemes,” or any other forms of solicitation; (vii) upload, post, email, or otherwise transmit any material that contains software viruses or any other computer code, files, or programs designed to interrupt, destroy, or limit the functionality of any computer software or hardware or telecommunications equipment; (viii) interfere with or disrupt the Application Services or servers or networks connected to the Application Services, or disobey any requirements, procedures, policies or regulations of networks connected to the Application Services; (ix) intentionally or unintentionally violate any applicable local, state, national or international law or regulation; (x) “stalk” or otherwise harass another; or (xi) collect or store personal data about other users.
      h3 7. USE POLICIES
      p
        | Customer is solely responsible for any content and other material that Customer submits, publishes, transmits, or displays on, through, or with the Application Services.
      p
        | The Application Services we may provide or make available to Customer may be subject to U.S. export control and economic sanctions laws. Customer agrees to comply with all such laws and regulations as they relate to access to and use of the Application Services. Customer shall not access or use the Application Services if Customer is located in any jurisdiction in which the provision of the Application Services is prohibited under U.S. or other applicable laws or regulations (a 
        strong “Prohibited Jurisdiction”
        | ) and Customer shall not provide access to the Application Services to any government, entity or individual located in any Prohibited Jurisdiction. Customer represents, warrants and covenants that (a) Customer is not named on any U.S. government list of persons or entities prohibited from receiving U.S. exports, or transacting with any U.S. person; (b) Customer is not a national of, or a company registered in, any Prohibited Jurisdiction; (c) Customer shall not permit its Authorized Users or any agents to access or use the Application Services in violation of any U.S. or other applicable export embargoes, prohibitions or restrictions; and (d) Customer shall comply with all applicable laws regarding the transmission of technical data exported from the United States and the country in which Customer, its Authorized Users and its agents are located.
      h3 8. EMAIL AND MESSAGES RELATED RULES
      p
        | Customer agrees to the following while using Mixpanel’s Messages service (which is described at 
        
        |  and which enables Customer to send targeted emails, notifications or messages):
      p a. Customer will not use purchased, scraped, or illegally obtained email lists;
      p b. Customer will not use rented email lists (even if they “opted in”);
      p c. Customer will not use third party email lists whatsoever;
      p
        | d. Customer will not send Spam or Unsolicited Bulk Email, as defined by Spamhaus at 
        
        
        | .
      p
        | e. Customer will abide by the CAN-SPAM Act of 2003, as amended, and all applicable, state, federal, or international anti-spam laws, rules and regulations, including email laws relating to consent, opt-out methods and processing, notices, and emails sent to email addresses with wireless domains; and agrees that Customer, and not Mixpanel, is responsible for determining whether the Mixpanel Messages service will be suitable for Customer’s compliance obligations. Customer will not send emails or messages promoting illegal activity or offering to sell illegal substances.
      p
        | f. Customer will abide by Apple’s and/or Android’s terms of use requirements and restrictions regarding push notifications.
      h3 9. TRADEMARKS AND PUBLICITY
      p
        | “Mixpanel,” the Mixpanel logo, and any other product or service name or slogan displayed on the Application Services are trademarks of Mixpanel, Inc. or its affiliates, and its suppliers or licensors, and may not be copied, imitated or used, in whole or in part, without the prior written permission of Mixpanel or the applicable trademark holder. Customer shall not use any metatags or any other “hidden text” utilizing “Mixpanel” or any other name, trademark or product or service name of Mixpanel without prior written permission. In addition, the look and feel of the Application Services, including all page headers, custom graphics, button icons and scripts, is the service mark, trademark and/or trade dress of Mixpanel and may not be copied, imitated or used, in whole or in part, without prior written permission. All other trademarks, registered trademarks, product names and company names or logos mentioned in the Application Services are the property of their respective owners. Reference to any products, services, processes or other information, by trade name, trademark, manufacturer, supplier, or otherwise does not constitute or imply endorsement, sponsorship, or recommendation thereof by Mixpanel.
      p
        | Customer agrees to allow Mixpanel, and hereby does provide Mixpanel with the necessary rights and licenses, to use Customer’s name and logo on the Mixpanel website, blog and/or in marketing materials, including case studies and as press references, to identify Customer as a customer of Mixpanel.  Customer agrees to act as a customer reference for the Application Services and Customer agrees to respond reasonably to all such reference contacts.
      h3 10. CONFIDENTIAL INFORMATION; FEEDBACK
      p
        | 10.1 “
        em
          strong Confidential Information
        | ” shall mean all written or oral information, disclosed by either party to the other, related to the operations of either party or a third party that has been identified as confidential or that by the nature of the circumstances surrounding disclosure ought reasonably to be treated as confidential. The parties acknowledge that during the performance of this Agreement, each party will have access to certain of the other party’s Confidential Information or Confidential Information of third parties that the disclosing party is required to maintain as confidential. Both parties agree that all items of Confidential Information are proprietary to the disclosing party or such third party, as applicable, and will remain the sole property of the disclosing party or such third party.
      p
        | 10.2 Each party agrees as follows: (a) to use Confidential Information disclosed by the other party only for the purposes described herein; (b) that such party will not reproduce Confidential Information disclosed by the other party, and will hold in confidence and protect such Confidential Information from dissemination to, and use by, any third party; (c) that neither party will create any derivative work from Confidential Information disclosed to such party by the other party; (d) to restrict access to the Confidential Information disclosed by the other party to such of its personnel, agents, and/or consultants, if any, who have a need to have access and who have been advised of and have agreed in writing to treat such information in accordance with the terms of this Agreement; and (e) to the extent practicable, return or destroy all Confidential Information disclosed by the other party that is in its possession upon termination or expiration of this Agreement, upon request of the other party.
      p
        | 10.3 Notwithstanding the foregoing, the provisions of Sections 10.1 and 10.2 will not apply to Confidential Information that (a) is publicly available or in the public domain at the time disclosed; (b) is or becomes publicly available or enters the public domain through no fault of the recipient; (c) is rightfully communicated to the recipient by persons not bound by confidentiality obligations with respect thereto; (d) is already in the recipient’s possession free of any confidentiality obligations with respect thereto at the time of disclosure; (e) is independently developed by the recipient; or (f) is approved for release or disclosure by the disclosing party without restriction. Notwithstanding the foregoing, each party may disclose Confidential Information to the limited extent required (x) in order to comply with the order of a court or other governmental body, or as otherwise necessary to comply with applicable law, provided that, to the extent permitted by law, the party making the disclosure pursuant to the order shall first have given written notice to the other party and made a reasonable effort to obtain a protective order; or (y) to establish a party’s rights under this Agreement, including to make such court filings as it may be required to do.
      p
        | 10.4 If Customer or its Authorized Users provide Mixpanel any suggestions, recommendations, or other feedback relating to Mixpanel’s current or future products or services (“
        em
          strong Feedback
        | ”), Mixpanel shall have the right to use the Feedback in any manner, including but not limited to future enhancements and modifications to the Application Services. Customer hereby grants to Mixpanel and its assigns a perpetual, worldwide, fully transferable, sublicensable, fully paid-up, irrevocable, royalty free license to use, reproduce, modify, create derivative works from, distribute, and display the Feedback in any manner any for any purpose, in any media, software, or technology of any kind now existing or developed in the future, without any obligation to provide attribution or compensation to Customer or any third party.  In addition, Mixpanel shall be free to reuse all general knowledge, experience, know-how, works and technologies (including ideas, concepts, processes and techniques) related to or acquired during provision of the Application Services.
      h3 11. WARRANTIES; DISCLAIMER OF WARRANTIES
      p
        | 11.1 Mixpanel warrants to Customer that the Application Services will perform materially in accordance with the documentation that accompany or is available for the Application Services by Mixpanel.  Mixpanel’s sole liability and Customer’s exclusive right and remedy for a breach of the foregoing warranty is for Mixpanel to correct or re-perform the nonconforming Application Services.
      p
        | 11.2 Customer warrants that Customer owns or has obtained all necessary rights, title and interest, and obtained all necessary consents, to transfer the Customer Data to Mixpanel and its data center provider(s) for the purpose of processing such Customer Data in accordance with this Agreement.
      p
        | 11.3 EXCEPT AS SPECIFICALLY PROVIDED HEREIN, USE OF SERVICES PROVIDED BY MIXPANEL INCLUDING BUT NOT LIMITED TO THE APPLICATION SERVICES, ANY PROFESSIONAL SERVICES AND CUSTOMER SUPPORT SERVICES IS AT CUSTOMER’S SOLE RISK. SUCH SERVICES ARE PROVIDED ON AN “AS IS” AND “AS AVAILABLE” BASIS. MIXPANEL AND ITS SUPPLIERS AND LICENSORS EXPRESSLY DISCLAIM ALL WARRANTIES OF ANY KIND, WHETHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO THE IMPLIED INDEMNITIES AND WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE, AND NON-INFRINGEMENT. MIXPANEL DOES NOT GUARANTEE THE ACCURACY, COMPLETENESS, OR USEFULNESS OF ITS SERVICES, AND CUSTOMER RELIES ON SUCH SERVICES AT CUSTOMER’S OWN RISK.  NEITHER DOES MIXPANEL GUARANTEE THE ACCURACY, USABILITY, COMPLETENESS, OR USEFULNESS OF ANY CUSTOM REPORT, AND CUSTOMER USES CUSTOM REPORTING FEATURES AT CUSTOMER’S OWN RISK. ANY MATERIAL THAT CUSTOMER ACCESSES OR OBTAINS THROUGH MIXPANEL’S SERVICES, INCLUDING CUSTOMER CONTENT, IS DONE AT CUSTOMER’S OWN DISCRETION AND RISK AND CUSTOMER WILL BE SOLELY RESPONSIBLE FOR ANY DAMAGE TO CUSTOMER’S COMPUTER OR LOSS OF DATA THAT RESULTS FROM THE DOWNLOAD OF ANY MATERIAL THROUGH MIXPANEL’S SERVICES. NO ADVICE OR INFORMATION, WHETHER ORAL OR WRITTEN, OBTAINED BY CUSTOMER FROM MIXPANEL OR THROUGH OR FROM THE APPLICATION SERVICES WILL CREATE ANY WARRANTY NOT EXPRESSLY STATED IN THIS AGREEMENT.
      h3 12. LIMITATION OF LIABILITY
      p
        | MIXPANEL AND ITS SUPPLIERS AND LICENSORS WILL NOT BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR EXEMPLARY DAMAGES, INCLUDING BUT NOT LIMITED TO, DAMAGES FOR LOSS OF PROFITS, GOODWILL, USE, DATA, OR OTHER INTANGIBLE LOSSES (EVEN IF MIXPANEL HAS BEEN ADVISED OF THE POSSIBILITY OF THESE DAMAGES), RESULTING FROM CUSTOMER’S USE OF THE APPLICATION SERVICES OR MIXPANEL’S PROVISION OF ANY OTHER SERVICES. UNDER NO CIRCUMSTANCES WILL THE TOTAL LIABILITY OF MIXPANEL AND ITS SUPPLIERS AND LICENSORS OF ALL KINDS ARISING OUT OF OR RELATED TO CUSTOMER’S USE OF THE APPLICATION SERVICES (INCLUDING BUT NOT LIMITED TO WARRANTY CLAIMS) OR MIXPANEL’S PROVISION OF ANY OTHER SERVICES, REGARDLESS OF THE FORUM AND REGARDLESS OF WHETHER ANY ACTION OR CLAIM IS BASED ON CONTRACT, TORT, NEGLIGENCE OR OTHERWISE, EXCEED THE AMOUNTS, IF ANY, THAT CUSTOMER HAS PAID TO MIXPANEL FOR CUSTOMER’S USE OF THE APPLICATION SERVICES FOR THE TWELVE (12) MONTH PERIOD PRIOR TO THE CLAIM.
      h3 13. INDEMNITY
      p
        | Customer will defend, indemnify and hold harmless Mixpanel, its suppliers and licensors, and its respective subsidiaries, affiliates, officers, agents, employees, representatives, and assigns, from any costs, damages, expenses, and liability caused by Customer’s use of the Application Services, Customer’s violation of this Agreement, Customer Content, or Customer’s violation of any rights of a third party through use of the Application Services.
      h3 14. MISCELLANEOUS
      p
        | 14.1 Enforcement of any dispute relating to this Agreement will be governed by the laws of the State of California, excluding its conflict and choice of law principles. For parties residing in the United States, the exclusive jurisdiction and venue for any claims arising out of or related to this Agreement or Customer’s use of the Application Services is in the state and federal courts located in City and County of San Francisco, California, and Customer irrevocably agrees to submit to the jurisdiction of such courts.
      p
        | 14.2 Mixpanel’s failure to enforce any right or provision in this Agreement will not constitute a waiver of such right or provision unless acknowledged and agreed to by Mixpanel in writing. In the event that a court of competent jurisdiction finds any provision of this Agreement to be illegal, invalid, or unenforceable, the remaining provisions will remain in full force and effect.
      p
        | 14.3 The terms and conditions which by their nature are intended to survive termination of this Agreement shall survive, including Restrictions, Disclaimer of Warranties, Feedback, Indemnity, and Limitation of Liability.  This Agreement contains the entire understanding of the parties on the subject matter hereof.
      p
        | 14.4 If Customer is a U.S. federal government department or agency or contracting on behalf of such department or agency, the Application Services are a “Commercial Item” as that term is defined at 48 C.F.R. §2.101, consisting of “Commercial Computer Software” and “Commercial Computer Software Documentation,” as those terms are used in 48 C.F.R. §12.212 or 48 C.F.R. §227.7202.  Consistent with 48 C.F.R. §12.212 or 48 C.F.R. §227.7202-1 through 227.7202-4, as applicable, the Application Services are licensed to Customer with only those rights as provided under the terms and conditions of this Agreement.
      h3 15. CONTACTING US
      p
        | All notices to be provided by Mixpanel to Customer under this Agreement may be delivered in writing (a) by nationally recognized overnight delivery service (“
        em
          strong Courier
        | ”) or U.S. mail to the contact mailing address provided by Customer on any Order Form; or (b) by electronic mail to the electronic mail address provided for Customer’s account owner.  If you need to give notice to Mixpanel, you must do so in writing by Courier or U.S. mail to 405 Howard Street, 2
        sup nd
        |  Floor, San Francisco, CA 94105, Attn: Legal Department.  All notices shall be deemed to have been given immediately upon delivery if by electronic mail; or, if otherwise delivered, then upon the earlier of receipt or two (2) business days after being deposited in the mail or with a Courier as permitted above.  If you have any questions or concerns about the Application Services or this Agreement, you may contact us by email at 
        | .

</template>

<script>
export default {
  name: 'PagePolicy'
}
</script>

<style lang="scss" scoped>
  @import '../../scss/base';
  .page_policy {
    padding: 3rem;
    height: 100vh;
    background: linear-gradient(0deg, #23252A -1.66%, #2D2F35 100%);
    overflow: auto;
  }
</style>
