<#import "template.ftl" as layout>
<#import "terms-and-conditions.ftl" as terms>
<@layout.registrationLayout; section>
    <#if section = "header">
        ${msg("registerTitle")}
    <#elseif section = "form">
        <@terms.termsAndConditionsHtml></@terms.termsAndConditionsHtml>
        <form id="kc-register-form" class="${properties.kcFormClass!}" action="${url.registrationAction}" method="post">
            <div class="${properties.kcFormGroupClass!} ${messagesPerField.printIfExists('firstName',properties.kcFormGroupErrorClass!)}">
                <#--  <div class="${properties.kcLabelWrapperClass!}">
                    <label for="firstName" class="${properties.kcLabelClass!}">${msg("firstName")}</label>
                </div>  -->
                <div class="${properties.kcInputWrapperClass!}">
                    <input placeholder="${msg("firstName")}" type="text" id="firstName" class="${properties.kcInputClass!}" name="firstName" value="${(register.formData.firstName!'')}" />
                </div>
            </div>

            <div class="${properties.kcFormGroupClass!} ${messagesPerField.printIfExists('lastName',properties.kcFormGroupErrorClass!)}" >
                <#--  <div class="${properties.kcLabelWrapperClass!}">
                    <label for="lastName" class="${properties.kcLabelClass!}">${msg("lastName")}</label>
                </div>  -->
                <div class="${properties.kcInputWrapperClass!}">
                    <input placeholder="${msg("lastName")}" type="text" id="lastName" class="${properties.kcInputClass!}" name="lastName" value="${(register.formData.lastName!'')}" />
                </div>
            </div>

            <div class="${properties.kcFormGroupClass!} ${messagesPerField.printIfExists('email',properties.kcFormGroupErrorClass!)}">
                <#--  <div class="${properties.kcLabelWrapperClass!}">
                    <label for="email" class="${properties.kcLabelClass!}">${msg("email")}</label>
                </div>  -->
                <div class="${properties.kcInputWrapperClass!}">
                    <input placeholder="${msg("email")}" type="text" id="email" class="${properties.kcInputClass!}" name="email" value="${(register.formData.email!'')}" autocomplete="email" />
                </div>
            </div>

          <#if !realm.registrationEmailAsUsername>
            <div class="${properties.kcFormGroupClass!} ${messagesPerField.printIfExists('username',properties.kcFormGroupErrorClass!)}">
                <#--  <div class="${properties.kcLabelWrapperClass!}">
                    <label for="username" class="${properties.kcLabelClass!}">${msg("username")}</label>
                </div>  -->
                <div class="${properties.kcInputWrapperClass!}">
                    <input placeholder="${msg("username")}" type="text" id="username" class="${properties.kcInputClass!}" name="username" value="${(register.formData.username!'')}" autocomplete="username" />
                </div>
            </div>
          </#if>

            <#if passwordRequired??>
            <div class="${properties.kcFormGroupClass!} ${messagesPerField.printIfExists('password',properties.kcFormGroupErrorClass!)}">
                <#--  <div class="${properties.kcLabelWrapperClass!}">
                    <label for="password" class="${properties.kcLabelClass!}">${msg("password")}</label>
                </div>  -->
                <div class="${properties.kcInputWrapperClass!}">
                    <input placeholder="${msg("password")}" type="password" id="password" class="${properties.kcInputClass!}" name="password" autocomplete="new-password"/>
                </div>
            </div>

            <div class="${properties.kcFormGroupClass!} ${messagesPerField.printIfExists('password-confirm',properties.kcFormGroupErrorClass!)}">
                <#--  <div class="${properties.kcLabelWrapperClass!}">
                    <label for="password-confirm" class="${properties.kcLabelClass!}">${msg("passwordConfirm")}</label>
                </div>  -->
                <div class="${properties.kcInputWrapperClass!}">
                    <input placeholder="${msg("passwordConfirm")}" type="password" id="password-confirm" class="${properties.kcInputClass!}" name="password-confirm" />
                </div>
            </div>
            </#if>

            <div class="form-group">
                <div class="${properties.kcLabelWrapperClass!}" style="display:none">
                    <label for="user.attributes.firstlogin" class="${properties.kcLabelClass!}">First login</label>
                </div>

                <div class="${properties.kcInputWrapperClass!}" style="display:none">
                    <input type="text" class="${properties.kcInputClass!}" id="user.attributes.firstlogin" name="user.attributes.firstlogin" value="true"/>
                </div>
            </div>

            <div class="form-group">
                <div class="${properties.kcLabelWrapperClass!}" style="display:none">
                    <label for="user.attributes.questionnaire" class="${properties.kcLabelClass!}">Questionnaire</label>
                </div>

                <div class="${properties.kcInputWrapperClass!}" style="display:none">
                    <input type="text" class="${properties.kcInputClass!}" id="user.attributes.questionnaire" name="user.attributes.questionnaire" value="false"/>
                </div>
            </div>


            <div class="${properties.kcFormGroupClass!} ${messagesPerField.printIfExists('termsAndConditions',properties.kcFormGroupErrorClass!)}">
                <div style="color: #fff" class="${properties.kcInputWrapperClass!}">
                    <input id="termsAndConditions" name="termsAndConditions" type="checkbox" checked>
                    <span class="terms-and-conditions-text">I agree to</span>
                    <span id="terms-and-condition-link" class="terms-and-conditions-text-link"> ${msg("termsAndConditions")} </span>
                </div>
            </div>

            <#if recaptchaRequired??>
            <div class="form-group">
                <div class="${properties.kcInputWrapperClass!}">
                    <div class="g-recaptcha" data-size="compact" data-sitekey="${recaptchaSiteKey}"></div>
                </div>
            </div>
            </#if>

            <div class="${properties.kcFormGroupClass!}">
                <div id="kc-form-options" class="${properties.kcFormOptionsClass!}">
                    <div class="${properties.kcFormOptionsWrapperClass!}">
                        <span><a href="${url.loginUrl}">${kcSanitize(msg("backToLogin"))?no_esc}</a></span>
                    </div>
                </div>

                <div id="kc-form-buttons" class="${properties.kcFormButtonsClass!}">
                    <input id="register-submit-btn" class="${properties.kcButtonClass!} ${properties.kcButtonPrimaryClass!} ${properties.kcButtonBlockClass!} ${properties.kcButtonLargeClass!}" type="submit" value="${msg("doRegister")}"/>
                </div>
            </div>
        </form>
    </#if>
</@layout.registrationLayout>
