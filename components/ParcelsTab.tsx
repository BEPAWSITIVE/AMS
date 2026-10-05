"use client";
import { useState, useEffect } from "react";
import { supabase, Parcel } from "@/lib/supabase";
import { localdb } from "@/lib/localdb";
import { X, Package, Search, Camera, Clock, CheckCircle2 } from "lucide-react";

export default function ParcelsTab() {
  const [parcels, setParcels] = useState<Parcel[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  
  // Form States
  const [companyName, setCompanyName] = useState("");
  const [recipientName, setRecipientName] = useState("");
  const [barcode, setBarcode] = useState("");
  const [documentFile, setDocumentFile] = useState<File | null>(null);

  // Pickup Modal
  const [pickupModal, setPickupModal] = useState<Parcel | null>(null);
  const [pickerName, setPickerName] = useState("");

  useEffect(() => {
    fetchParcels();
    
    const channel = supabase
      .channel('parcels_changes')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'parcels' },
        () => fetchParcels()
      )
      .subscribe();

    const interval = setInterval(() => {
      if (navigator.onLine) fetchParcels();
    }, 30000);

    return () => {
      supabase.removeChannel(channel);
      clearInterval(interval);
    };
  }, []);

  async function fetchParcels() {
    let allParcels: Parcel[] = [];
    if (navigator.onLine) {
      const { data, error } = await supabase.from('parcels').select('*').order('received_at', { ascending: false });
      if (!error && data) {
        allParcels = data;
        localStorage.setItem('cached_parcels', JSON.stringify(data));
      }
    } else {
      const cached = localStorage.getItem('cached_parcels');
      if (cached) allParcels = JSON.parse(cached);
    }
    
    const queuedParcels = await localdb.parcelQueue.toArray();
    const merged = [...queuedParcels, ...allParcels].reduce((acc, curr) => {
      const idx = acc.findIndex(item => item.id === curr.id);
      if (idx === -1) {
        acc.push(curr);
      } else if (queuedParcels.find(q => q.id === curr.id)) {
        acc[idx] = curr;
      }
      return acc;
    }, [] as Parcel[]);
    
    merged.sort((a, b) => new Date(b.received_at).getTime() - new Date(a.received_at).getTime());
    setParcels(merged);
    setLoading(false);
  }

  const handleOpenForm = () => {
    setCompanyName("");
    setRecipientName("");
    setBarcode("");
    setDocumentFile(null);
    setShowForm(true);
  };

  const handleReceiveParcel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyName || !recipientName) return;
    
    setIsUploading(true);
    let photo_url = "";
    const parcelId = crypto.randomUUID();
    
    if (documentFile) {
      if (!navigator.onLine) {
        alert("You must be online to upload parcel photos.");
        setIsUploading(false);
        return;
      }
      try {
        const fileExt = documentFile.name.split('.').pop() || 'jpg';
        const fileName = `${parcelId}_${Date.now()}.${fileExt}`.replace(/\s+/g, '_');
        const { error } = await supabase.storage.from('parcels').upload(fileName, documentFile, { cacheControl: '3600', upsert: false });
        if (error) throw error;
        const { data: { publicUrl } } = supabase.storage.from('parcels').getPublicUrl(fileName);
        photo_url = publicUrl;
      } catch (err: any) {
        alert("Upload failed. Error: " + err.message);
        setIsUploading(false);
        return;
      }
    }
    
    const newParcel: Parcel = {
      id: parcelId,
      company_name: companyName,
      recipient_name: recipientName,
      barcode: barcode || undefined,
      photo_url: photo_url || undefined,
      received_at: new Date().toISOString(),
      status: 'At Gate'
    };
    
    if (navigator.onLine) {
      try {
        const { error } = await supabase.from('parcels').insert([newParcel]);
        if (error) throw error;
      } catch (err: any) {
        alert("Error adding parcel: " + err.message);
        setIsUploading(false);
        return;
      }
    } else {
      await localdb.parcelQueue.put(newParcel);
    }
    
    setIsUploading(false);
    setShowForm(false);
    fetchParcels();
  };

  const handlePickupSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pickupModal || !pickerName) return;

    const updatedParcel: Parcel = {
      ...pickupModal,
      status: 'Picked Up',
      picked_up_by: pickerName,
      picked_up_at: new Date().toISOString()
    };

    if (navigator.onLine) {
      await supabase.from('parcels').update(updatedParcel).eq('id', updatedParcel.id);
    } else {
      await localdb.parcelQueue.put(updatedParcel);
    }

    setPickupModal(null);
    setPickerName("");
    fetchParcels();
  };

  const formatTime = (isoString: string) => {
    const d = new Date(isoString);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' on ' + d.toLocaleDateString([], { month: 'short', day: 'numeric' });
  };

  const activeParcels = parcels.filter(p => p.status === 'At Gate');
  const pastParcels = parcels.filter(p => p.status === 'Picked Up');

  return (
    <div className="p-4 pb-24 max-w-md mx-auto space-y-6">
      
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Parcels</h2>
          <p className="text-xs text-gray-500 font-medium">Gate Deliveries</p>
        </div>
        <button 
          onClick={handleOpenForm}
          className="bg-purple-600 text-white px-4 py-2 rounded-xl text-sm font-bold flex items-center shadow-md shadow-purple-200 active:scale-95 transition-transform"
        >
          + Receive Parcel
        </button>
      </div>

      {showForm && (
        <div className="bg-white p-5 rounded-3xl shadow-xl border border-gray-100 animate-fade-in relative">
          <button onClick={() => setShowForm(false)} className="absolute top-4 right-4 text-gray-400 hover:text-gray-700 bg-gray-50 p-1.5 rounded-full">
            <X size={18} />
          </button>
          
          <div className="flex items-center space-x-3 mb-6">
            <div className="bg-purple-100 p-2.5 rounded-xl text-purple-600">
              <Package size={20} />
            </div>
            <h3 className="text-lg font-bold text-gray-800">Receive New Parcel</h3>
          </div>
          
          <form onSubmit={handleReceiveParcel} className="space-y-4">
            
            <div className="flex space-x-3">
              <div className="w-1/2">
                <label className="block text-xs font-bold text-gray-500 mb-1">Company *</label>
                <input 
                  type="text" 
                  value={companyName} 
                  onChange={e => setCompanyName(e.target.value)}
                  placeholder="Amazon, Flipkart..."
                  className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-purple-500"
                  required
                />
              </div>
              <div className="w-1/2">
                <label className="block text-xs font-bold text-gray-500 mb-1">For Whom *</label>
                <input 
                  type="text" 
                  value={recipientName} 
                  onChange={e => setRecipientName(e.target.value)}
                  placeholder="Employee Name"
                  className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-purple-500"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-500 mb-1">Barcode / Tracking #</label>
              <div className="relative">
                <Search className="absolute left-3 top-3.5 text-gray-400" size={16} />
                <input 
                  type="text" 
                  value={barcode} 
                  onChange={e => setBarcode(e.target.value)}
                  placeholder="Scan or type barcode"
                  className="w-full bg-gray-50 border border-gray-200 p-3 pl-9 rounded-xl outline-none focus:ring-2 focus:ring-purple-500 font-mono"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-500 mb-1">Photo of Parcel (Optional)</label>
              <div className="relative w-full bg-purple-50 border-2 border-dashed border-purple-200 p-4 rounded-xl text-center hover:bg-purple-100 transition-colors">
                <input 
                  type="file" 
                  accept="image/*"
                  capture="environment"
                  onChange={e => e.target.files && setDocumentFile(e.target.files[0])}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <div className="text-purple-600 font-bold flex flex-col items-center justify-center w-full">
                  {documentFile ? (
                    <>
                      <CheckCircle2 size={28} className="mb-1 text-green-500" />
                      <span className="text-green-600 text-sm">Photo Captured!</span>
                      <span className="text-xs text-gray-500 mt-1 max-w-full truncate px-4 font-medium">{documentFile.name}</span>
                    </>
                  ) : (
                    <>
                      <Camera size={28} className="mb-1" />
                      <span className="text-sm">Tap to Snap Photo</span>
                    </>
                  )}
                </div>
              </div>
            </div>

            <button 
              type="submit" 
              disabled={isUploading}
              className="w-full bg-purple-600 text-white py-3.5 rounded-xl font-bold shadow-md shadow-purple-200 disabled:opacity-50 mt-2"
            >
              {isUploading ? "Saving..." : "Save & Receive at Gate"}
            </button>
          </form>
        </div>
      )}

      {loading ? (
        <div className="text-center py-10 text-gray-400">Loading parcels...</div>
      ) : (
        <div className="space-y-6">
          
          {/* AWAITING PICKUP SECTION */}
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <Clock size={16} className="text-orange-500" />
              <h3 className="font-bold text-gray-800 text-sm uppercase tracking-wide">Awaiting Pickup ({activeParcels.length})</h3>
            </div>
            
            {activeParcels.length === 0 ? (
              <div className="text-center py-6 text-gray-400 bg-white rounded-2xl border border-dashed border-gray-200 text-sm">
                No parcels at the gate.
              </div>
            ) : (
              <div className="space-y-3">
                {activeParcels.map(p => (
                  <div 
                    key={p.id} 
                    onClick={() => setPickupModal(p)}
                    className="bg-white p-4 rounded-2xl shadow-sm border border-orange-100 hover:border-purple-300 cursor-pointer transition-colors relative overflow-hidden group"
                  >
                    <div className="absolute top-0 right-0 bg-orange-100 text-orange-600 text-[10px] font-bold px-2 py-1 rounded-bl-lg">
                      AT GATE
                    </div>
                    
                    <div className="flex justify-between items-start pr-12">
                      <div>
                        <h4 className="font-bold text-gray-800 text-lg">{p.recipient_name}</h4>
                        <p className="text-purple-600 font-bold text-xs uppercase tracking-wider">{p.company_name}</p>
                      </div>
                    </div>
                    
                    <div className="mt-3 bg-gray-50 rounded-lg p-2 text-xs text-gray-500 flex justify-between items-center">
                      <span>Rec: {formatTime(p.received_at)}</span>
                      {p.barcode && <span className="font-mono bg-white px-1.5 py-0.5 rounded border border-gray-200">{p.barcode}</span>}
                    </div>
                    
                    <div className="mt-2 text-center text-xs font-bold text-purple-500 opacity-0 group-hover:opacity-100 transition-opacity">
                      Tap to authorize pickup &rarr;
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* PAST PARCELS SECTION */}
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <CheckCircle2 size={16} className="text-green-500" />
              <h3 className="font-bold text-gray-800 text-sm uppercase tracking-wide">Recently Picked Up</h3>
            </div>
            
            <div className="space-y-3">
              {pastParcels.slice(0, 10).map(p => (
                <div key={p.id} className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 opacity-75">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-bold text-gray-700">{p.recipient_name}</h4>
                      <p className="text-gray-500 font-bold text-xs uppercase tracking-wider">{p.company_name}</p>
                    </div>
                    {p.photo_url && (
                      <a href={p.photo_url} target="_blank" rel="noreferrer" className="bg-gray-100 text-gray-500 p-1.5 rounded-lg hover:text-blue-500">
                        <Camera size={16} />
                      </a>
                    )}
                  </div>
                  
                  <div className="mt-3 bg-green-50 border border-green-100 rounded-lg p-2.5">
                    <p className="text-xs text-green-800 font-medium">
                      Picked up by <span className="font-bold">{p.picked_up_by}</span>
                    </p>
                    <p className="text-[10px] text-green-600 font-bold uppercase tracking-wider mt-0.5">
                      {p.picked_up_at && formatTime(p.picked_up_at)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
        </div>
      )}

      {/* Pickup Modal */}
      {pickupModal && (
        <div className="fixed inset-0 z-[120] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-white w-full max-w-sm rounded-3xl overflow-hidden shadow-2xl relative">
            <div className="bg-purple-600 p-6 text-white text-center">
              <Package size={40} className="mx-auto mb-2 opacity-90" />
              <h3 className="text-xl font-bold">{pickupModal.recipient_name}</h3>
              <p className="opacity-80 text-sm font-bold tracking-widest uppercase mt-1">{pickupModal.company_name}</p>
            </div>
            
            <form onSubmit={handlePickupSubmit} className="p-6 space-y-4">
              <div className="bg-purple-50 text-purple-800 p-3 rounded-xl text-sm font-bold text-center mb-2">
                Authorize Parcel Pickup
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 mb-1">Name of Person Taking Parcel *</label>
                <input 
                  type="text" 
                  value={pickerName}
                  onChange={e => setPickerName(e.target.value)}
                  placeholder="e.g. Rahul from IT"
                  className="w-full bg-gray-50 border border-gray-200 p-3 rounded-xl outline-none focus:ring-2 focus:ring-purple-500"
                  required
                  autoFocus
                />
              </div>

              <div className="flex space-x-3 pt-2">
                <button 
                  type="button" 
                  onClick={() => { setPickupModal(null); setPickerName(""); }}
                  className="flex-1 bg-gray-100 text-gray-600 py-3 rounded-xl font-bold"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="flex-1 bg-purple-600 hover:bg-purple-700 text-white py-3 rounded-xl font-bold shadow-md"
                >
                  Confirm Pickup
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
