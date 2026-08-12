describe('register -> login -> create task -> complete task', () => {
  const password = 'SecurePassword123'
  const taskTitle = 'Submit algorithms assignment'

  it('covers the full task management journey for a new user', () => {
    const email = `e2e_${Date.now()}@example.com`

    // Register
    cy.visit('/register')
    cy.get('[data-testid=display-name-input]').type('E2E Student')
    cy.get('[data-testid=email-input]').type(email)
    cy.get('[data-testid=password-input]').type(password)
    cy.get('[data-testid=register-btn]').click()
    cy.url().should('include', '/dashboard')

    // Create a task and see its computed priority
    cy.get('[data-testid=nav-tasks]:visible').click()
    cy.url().should('include', '/tasks')

    cy.get('[data-testid=add-task-btn]').click()
    cy.get('[data-testid=task-title]').find('input').type(taskTitle)
    cy.get('[data-testid=due-date]').find('input').type('in 3 days')
    cy.get('[data-testid=submit-task]').click()

    cy.get('[data-testid=task-card]').should('have.length', 1)
    cy.get('[data-testid=priority-badge]').should('be.visible')

    // Transparent score breakdown
    cy.get('[data-testid=task-card]').first().click()
    cy.get('[data-testid=priority-score]').should('contain.text', 'Priority score')
    cy.get('[data-testid=close-task-detail]').click()

    // Complete the task
    cy.get('[data-testid=task-checkbox]').click()
    cy.get('[data-testid=task-card]').should('have.length', 0)

    cy.contains('button', 'Completed').click()
    cy.get('[data-testid=task-card]').should('have.length', 1)
    cy.contains(taskTitle).should('be.visible')

    // Persists across logout/login
    cy.get('[data-testid=logout-btn]').click()
    cy.url().should('include', '/login')

    cy.get('[data-testid=email-input]').type(email)
    cy.get('[data-testid=password-input]').type(password)
    cy.get('[data-testid=login-btn]').click()
    cy.url().should('include', '/dashboard')

    cy.get('[data-testid=nav-tasks]:visible').click()
    cy.contains('button', 'Completed').click()
    cy.contains(taskTitle).should('be.visible')
  })
})
