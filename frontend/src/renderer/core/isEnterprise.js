import axios from 'axios';
export default async () => {
  try {
    const res = await axios.get(`/is_enterprise`);
    return res.data.is_enterprise;
  } catch (err) {
    return false;
  }
}