describe("Model Training", () => {
    var observeDOM = (function () {
        var MutationObserver = window.MutationObserver || window.WebKitMutationObserver;

        return function (obj, callback) {
            if (!obj || obj.nodeType !== 1) return;

            if (MutationObserver) {
                // define a new observer
                var mutationObserver = new MutationObserver(callback)

                // have the observer observe foo for changes in children
                mutationObserver.observe(obj, { childList: true, subtree: true })
                return mutationObserver
            }

            // browser support fallback
            else if (window.addEventListener) {
                obj.addEventListener('DOMNodeInserted', callback, false)
                obj.addEventListener('DOMNodeRemoved', callback, false)
            }
        }
    })();

    const startTest = () => {
        cy.fixture("userCredentials").then((user) => {
            cy.kcLogin(user.email, user.password);
        });
        cy.deleteAllModels();
        cy.createMnistModel("Model 1");

        cy.visit("/");

        // Click Model 1
        cy.get(".models-list .models-list-row.model-list-item")
            .first()
            .find(".column-1 .model-name-wrapper")
            .click();

        // Run with current settings
        cy.get('.main_toolbar button').contains('Run with current settings').click();
    }



    describe('tests while training', () => {

        before(() => {
            startTest();
        });

        it('should open statistics', () => {
            cy.get('.project-sidebar .nav-link').eq(1).should('not.have.class', 'is-active');
            cy.get(".project-sidebar .nav-link").eq(2).should('have.class', 'is-active');
        });

        it('should have no spinners', () => {
            cy.get('.chart-spinner').should('not.exist');
        });

        it('should change view box when clicking on a component', () => {
            cy.document().then((doc) => {
                const observer = cy.stub();
                observeDOM(doc.querySelector('.network_info-section.the-view-box .info-section_main'), observer)

                cy.get('#networkWorkspace .network-field .net-element')
                    .its("length").then((elementCount) => {
                        for (let i = 0; i < elementCount; i++) {
                            cy.get('#networkWorkspace .network-field').find('.net-element').eq(i).click().then(() => {
                                expect(observer).to.be.called;
                            })
                        }
                    })
            });
        });

        it('should change top view when clicking on a tab', () => {
            cy.document().then((doc) => {
                const observer = cy.stub();
                observeDOM(doc.querySelector('.network_info-section.the-statistics .info-section_main'), observer)

                cy.get('.statistics-box_tabset.statistics-tabs li')
                    .its("length").then((elementCount) => {
                        for (let i = 1; i < elementCount; i++) {
                            cy.get('.statistics-box_tabset.statistics-tabs li').eq(i).click().then(() => {
                                expect(observer).to.be.called;
                            })
                        }
                    })
            });
        });
    });

    describe('stop tests before finish', () => {
        before(() => {
            // click stop button
            cy.get(".toolbar-button-group .btn-menu-bar").eq(1).click();
        });

        it('should stop test when click stop button', () => {
            cy.get('.page_toolbar .toolbar-section .show-status-inline .name').should('have.text', 'Stopped');
            cy.get('.popup-global .popup .chart-spinner').should('not.exist');
            cy.get('.popup-global .settings-layer_section .body_results-info').should('exist');
        });
    });

    describe('wait until test finishes', () => {
        before(() => {
            startTest();
        });

        it('should show results when test finishes', () => {
            cy.get('.page_toolbar .toolbar-section .training-complete-text', { timeout: 100 * 1000 }).should('exist');
            cy.get('.popup-global .popup .chart-spinner').should('not.exist');
            cy.get('.popup-global .settings-layer_section .body_results-info').should('exist');
        })
    });
});