import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useStaffStore } from './staff'
import api from '../utils/api'

vi.mock('../utils/api')

describe('Staff Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should have initial isConfirmed state as false', () => {
    const store = useStaffStore()
    expect(store.isConfirmed).toBe(false)
  })

  it('should fetch confirm status', async () => {
    const store = useStaffStore()
    vi.mocked(api.get).mockResolvedValueOnce({ data: { is_confirmed: true } })
    
    await store.fetchConfirmStatus()
    
    expect(api.get).toHaveBeenCalledWith('/departments/confirm-status')
    expect(store.isConfirmed).toBe(true)
  })

  it('should confirm department data', async () => {
    const store = useStaffStore()
    vi.mocked(api.post).mockResolvedValueOnce({ data: { success: true } })
    
    const success = await store.confirmData()
    
    expect(api.post).toHaveBeenCalledWith('/departments/confirm')
    expect(success).toBe(true)
    expect(store.isConfirmed).toBe(true)
  })

  it('should automatically set isConfirmed to true when status is toggled', async () => {
    const store = useStaffStore()
    store.staffs = [{ id: 1, name: 'Test' }]
    vi.mocked(api.post).mockResolvedValue({ data: { success: true } })
    
    await store.toggleStaffStatus(1, 'bg-1')
    
    expect(store.isConfirmed).toBe(true)
  })

  it('should automatically set isConfirmed to true when applyToAll is called', async () => {
    const store = useStaffStore()
    store.staffs = [{ id: 1, name: 'Test' }]
    vi.mocked(api.post).mockResolvedValue({ data: { success: true } })
    vi.mocked(api.get).mockResolvedValue({ data: [] }) // for fetchStaffs
    
    await store.applyToAll('bg-2')
    
    expect(store.isConfirmed).toBe(true)
  })
})
