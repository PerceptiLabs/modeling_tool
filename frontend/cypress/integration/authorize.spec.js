it('Should authorize the user', () => {
  cy.visit('http://localhost:8080/');
  if(!sessionStorage.getItem("fileserver_token")) {
    cy.location('pathname', {timeout: 30000});
    cy.fixture('userCredentials').then((user)  => {
      cy.log(user);
      cy.login(user.email, user.password);
    })
  }
});