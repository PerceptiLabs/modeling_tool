let pathToSavedModel;
  it('Should save model with success', () => {
    cy.get('.workspace-scale_input input').type('{cmd}{shift}s');
    cy.get('.workspace-scale_input input').type('{ctrl}{shift}s');
    cy.get('.workspace-scale_input input').clear().type('100{enter}');

    cy.get('[data-testing-target="save-model-as-browse"]').click();

    cy.get('[data-testing-target="save-model-as-confirm-location"]:eq(1)').click();

    cy.get('[data-testing-target="save-model-as-path"]')
      .invoke('val')
      .then(path => {
        cy.log(path)
        cy.get('[data-testing-target="save-model-as-model-name"]')
          .invoke('val')
          .then(modelName => {
            cy.contains('Continue').click();
            cy.readFile(`${path}/${modelName}/model.json`).then(file => {
              cy.wrap(file).its('apiMeta.location').should('eq', path + '/' + modelName);
              cy.wrap(file).its('apiMeta.name').should('eq', modelName);
              pathToSavedModel = `${path}/${modelName}`;
            });
          });
      });
  })
  
  it('Should load the model with success', () => {
    cy.get('[data-testing-target="MenuItem_File"]')
        .invoke('attr', 'style', 'display: block')
    cy.contains("Import Model").click();
    cy.get('[data-testing-target="MenuItem_File"]')
        .invoke('attr', 'style', 'display: none')
    cy.get('[data-testing-target="import-model-path"]').type(pathToSavedModel, { force: true });
    cy.get('.popup_foot > :nth-child(2)').click();
  });