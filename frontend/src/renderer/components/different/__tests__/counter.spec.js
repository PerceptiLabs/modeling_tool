
import Counter from '../counter.vue';
import { render, fireEvent } from '@testing-library/vue';

test('It renders correctly', async () => {
  const { getByText } = render(Counter);
  getByText('Count: 0');
});


test('It adds correctly', async () => {
  const { getByText } = render(Counter);
  getByText('Count: 0');

  // Get buttons.
  const addButton = getByText('Add');

  // Click the Add button.
  await fireEvent.click(addButton);
  // Counter should be updated.
  getByText('Count: 1');
});


test('It subtracts correctly', async () => {
  const { getByText } = render(Counter);
  getByText('Count: 0');

  // Get buttons.
  const subtractButton = getByText('Subtract');

  // Click the subtract button.
  await fireEvent.click(subtractButton);

  // Counter should be updated.
  getByText('Count: -1');
});